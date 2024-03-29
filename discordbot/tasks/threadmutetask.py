"""Thread Mute Task."""

import asyncio
import datetime
import random
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.message_strings.thread_mute_reminders import MESSAGES
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class ThreadSpoilerTask(BaseTask):
    """Class for Thread spoiler task."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task at startup. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule(range(7), hours=[8], minute=10)
        self.task = self.thread_mute
        if start:
            self.task.start()

    @tasks.loop(count=1)
    async def thread_mute(self) -> None:
        """Task that sends daily "remember to mute this spoiler thread" messages."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        if now.hour != 8 or not (0 <= now.minute < 15):  # noqa: PLR2004
            self.logger.warning("Somehow task was started outside operational hours - %s", now)
            return

        if BSE_SERVER_ID not in [guild.id for guild in self.bot.guilds]:
            return

        self.logger.info("Checking spoiler threads for mute messages")
        all_threads = self.spoilers.get_all_threads(BSE_SERVER_ID)
        all_threads = [a for a in all_threads if a.active]

        for thread_info in all_threads:
            self.logger.info("Checking %s for spoiler message", thread_info.name)

            day = thread_info.day
            if now.weekday() != day:
                self.logger.info(
                    "Not the right day for %s: our day: %s, required: %s", thread_info.name, now.weekday(), day
                )
                # not the right day for this spoiler thread
                continue

            thread = await self.bot.fetch_channel(thread_info.thread_id)
            await thread.trigger_typing()

            message = random.choice(MESSAGES)

            # always add the config disclaimer to the end
            message += (
                "\n\nShow ended? The thread creator can use the `/config` command to "
                "disable mute reminders for this thread."
            )
            await thread.send(content=message, allowed_mentions=discord.AllowedMentions(everyone=True))
            self.logger.info("Sent message to %s, %s: %s", thread.id, thread.name, message)

    @thread_mute.before_loop
    async def before_thread_mute(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
