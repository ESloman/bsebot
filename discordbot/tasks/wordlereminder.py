
import asyncio
import datetime
import random

from logging import Logger


from discord.ext import tasks

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_BOT_ID
from discordbot.tasks.basetask import BaseTask


class WordleReminder(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.messages = [
            "Hey {mention}, don't forget to do your Wordle today!",
            "Don't forget to do your wordle today {mention}.",
            "{mention} hasn't done their Wordle today. Are they stupid?",
            "Daddy wants you to complete your Wordle today {mention}",
            "{mention}\nRoses are red\nViolets are blue\nI've done my Worlde\nDon't forget to do yours too!",
            "Hey {mention}, you absolute knob, you haven't done your Wordle yet!",
            "Guess what? {mention} is a fucking prick. Also, they didn't do their Wordle.",
            "Do your Wordle or die, {mention}."
        ]
        self.wordle_reminder.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.wordle_reminder.cancel()

    @tasks.loop(minutes=60)
    async def wordle_reminder(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """

        now = datetime.datetime.now()

        if now.hour != 19:
            return

        start = now - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)

        if not utilities.is_utc(now):
            # need to add UTC offset
            start = utilities.add_utc_offset(start)
            end = utilities.add_utc_offset(end)

        for guild in self.bot.guilds:

            guild_db = self.guilds.get_guild(guild.id)

            if not guild_db.get("wordle_reminders"):
                # guild isn't configured for wordle reminders
                return

            wordles_yesterday = self.interactions.query(
                {
                    "guild_id": guild.id,
                    "message_type": "wordle",
                    "timestamp": {"$gte": start, "$lte": end}
                }
            )

            _start = start + datetime.timedelta(days=1)
            _end = end + datetime.timedelta(days=1)
            wordles_today = self.interactions.query(
                {
                    "guild_id": guild.id,
                    "message_type": "wordle",
                    "timestamp": {"$gte": _start, "$lte": _end}
                }
            )

            today_ids = [m["user_id"] for m in wordles_today]

            reminders_needed = []
            for message in wordles_yesterday:
                user_id = message["user_id"]
                if user_id in today_ids:
                    # self.logger.info(f"{user_id} has already sent a wordle message today")
                    continue
                else:
                    # user hasn't done a wordle
                    reminders_needed.append(message)

            if not reminders_needed:
                self.logger.info("Everyone has done their wordle today!")
                continue

            for reminder in reminders_needed:
                if reminder["user_id"] == BSE_BOT_ID:
                    # skip bot reminder
                    continue
                channel = await self.bot.fetch_channel(reminder["channel_id"])
                await channel.trigger_typing()
                channel_id = reminder["channel_id"]

                if channel_id != channel.id:
                    self.logger.info(
                        f"{channel_id} for wordle message ({reminder['message_id']}) didn't match {channel.id}"
                    )
                    continue

                y_message = await channel.fetch_message(reminder["message_id"])

                message = random.choice(self.messages)
                message = message.format(mention=y_message.author.mention)

                self.logger.info(message)
                await y_message.reply(content=message)

    @wordle_reminder.before_loop
    async def before_wordle_reminder(self):
        """
        Make sure that websocket is open before we start querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
