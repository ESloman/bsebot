
import asyncio
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.tasks.basetask import BaseTask


class ThreadSpoilerTask(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.thread_mute
        self.task.start()

    @tasks.loop(minutes=15)
    async def thread_mute(self):
        """
        Task that sends daily "remember to mute this spoiler thread" messages.
        """

        now = datetime.datetime.now()
        if now.hour != 8 or not (0 <= now.minute < 15):
            return

        if BSE_SERVER_ID not in self.guild_ids:
            return

        self.logger.info("Checking spoiler threads for mute messages")
        all_threads = self.spoilers.get_all_threads(BSE_SERVER_ID)
        all_threads = [a for a in all_threads if a["active"]]

        for thread_info in all_threads:
            self.logger.info(f"Checking {thread_info['name']} for spoiler message")

            day = thread_info["day"]
            if now.weekday() != day:
                self.logger.info(
                    f"Not the right day for {thread_info['name']}: our day: {now.weekday()}, required: {day}"
                )
                # not the right day for this spoiler thread
                continue

            thread = await self.bot.fetch_channel(thread_info["thread_id"])
            await thread.trigger_typing()
            message = (
                "New episode today - remember to mute cuties xoxo\n\n"
                "Show ended? The thread creator can use the `/config` command to "
                "disable mute reminders for this thread."
            )
            await thread.send(content=message, allowed_mentions=discord.AllowedMentions(everyone=True))
            self.logger.info(f"Sent message to {thread.id}, {thread.name}: {message}")

    @thread_mute.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
