import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_BOT_ID, BSE_SERVER_ID, GENERAL_CHAT
from mongo.bsepoints import UserInteractions


class WordleReminder(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger, startup_tasks):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.startup_tasks = startup_tasks
        self.user_interactions = UserInteractions()
        self.wordle_reminder.start()

    def _check_start_up_tasks(self) -> bool:
        """
        Checks start up tasks
        """
        for task in self.startup_tasks:
            if not task.finished:
                return False
        return True

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
        if not self._check_start_up_tasks():
            self.logger.info("Startup tasks not complete - skipping loop")
            return
        now = datetime.datetime.now()

        if now.hour != 19:
            return

        if BSE_SERVER_ID not in self.guilds:
            return

        start = now - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)

        wordles_yesterday = self.user_interactions.query(
            {
                "message_type": "wordle",
                "timestamp": {"$gte": start, "$lte": end}
            }
        )

        _start = start + datetime.timedelta(days=1)
        _end = end + datetime.timedelta(days=1)

        wordles_today = self.user_interactions.query(
            {
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
            return

        channel = await self.bot.fetch_channel(GENERAL_CHAT)
        for reminder in reminders_needed:
            await channel.trigger_typing()
            if reminder["user_id"] == BSE_BOT_ID:
                # skip bot reminder
                continue
            channel_id = reminder["channel_id"]

            if channel_id != channel.id:
                self.logger.info(
                    f"{channel_id} for wordle message ({reminder['message_id']}) didn't match {GENERAL_CHAT}"
                )
                continue
            y_message = await channel.fetch_message(reminder["message_id"])

            msg = (
                f"Hey {y_message.author.mention}, don't forget to do your Wordle today!"
            )

            self.logger.info(msg)
            await y_message.reply(content=msg)

    @wordle_reminder.before_loop
    async def before_wordle_reminder(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
