"""BSEddies annual awards task."""

import asyncio
import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class AnnualBSEddiesAwards(BaseTask):
    """Class for annual bseddies awards."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task on startup. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule([], hours=[14], minute=15, dates=[datetime.datetime(2021, 1, 1)])
        self.task = self.annual_bseddies_awards
        if start:
            self.task.start()

    @tasks.loop(count=1)
    async def annual_bseddies_awards(self) -> None:
        """Task that checks if we need to do the Annual BSEddies Awards.

        This should only trigger on the 1st Jan. It will do annual stats and awards.
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if now.day != 1 or now.hour != 14 or now.month != 1:  # noqa: PLR2004
            # we only want to trigger on the first of each YEAR
            # and also trigger at 2pm
            self.logger.warning("Somehow task was started outside operational hours - %s", now)
            return

        if BSE_SERVER_ID not in [guild.id for guild in self.bot.guilds]:
            # does not support other servers yet
            return

        self.logger.info("Time for the annual BSEddies awards! %s", now)

        # set some kind of activity here
        activity = discord.Activity(
            name="with some annual stats and awards ",
            type=discord.ActivityType.playing,
            details="Working out annual BSEddies awards",
        )
        await self.bot.change_presence(activity=activity)

        # put a "BSEBot is typing..." message
        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
        await channel.trigger_typing()

        awards_builder = AwardsBuilder(self.bot, BSE_SERVER_ID, True)

        self.logger.debug("Calculating stats")
        stats, message = await awards_builder.build_stats_and_message()
        self.logger.debug("Calculating awards")
        awards, bseddies_awards = await awards_builder.build_awards_and_message()

        self.logger.debug("Logging to DB and sending messages")
        await awards_builder.send_stats_and_awards(stats, message, awards, bseddies_awards)

        # set activity back
        listening_activity = discord.Activity(
            name="conversations",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )
        await self.bot.change_presence(activity=listening_activity)

        self.logger.info("Sent messages! Until next year!")

    @annual_bseddies_awards.before_loop
    async def before_thread_mute(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
