
import asyncio
import datetime
from logging import Logger

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class RemindersTask(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.reminders
        self.task.start()

    @tasks.loop(minutes=1)
    async def reminders(self):
        """
        Loop that triggers reminders from the database
        """

        now = datetime.datetime.now()
        for guild in self.bot.guilds:

            open_reminders = self.server_reminders.get_open_reminders(guild.id)
            for reminder in open_reminders:
                if now > reminder["timeout"]:
                    # time to do reminder
                    channel = await guild.fetch_channel(reminder["channel_id"])
                    message = await channel.fetch_message(reminder["message_id"])

                    msg = (
                        f"Hey, <@{reminder['user_id']}>, don't forget about `{reminder['reason']}`!"
                    )

                    await message.reply(content=msg)
                    self.server_reminders.close_reminder(reminder["_id"])

    @reminders.before_loop
    async def before_reminders(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
