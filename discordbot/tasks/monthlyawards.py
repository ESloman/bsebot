"""Monthly BSEddies awards task."""

import asyncio
import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class MonthlyBSEddiesAwards(BaseTask):
    """Class for monthly bseddies awards."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task at startup. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule([], [11], 15, dates=[datetime.datetime(2021, x, 1) for x in range(1, 13)])
        self.task = self.bseddies_awards
        if start:
            self.task.start()

    @tasks.loop(count=1)
    async def bseddies_awards(self) -> None:
        """Loop that triggers our monthly awards.

        This will trigger on the 1st of a month. Calculates guild stats/awards.
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        # whether to run in debug mode or not
        debug = False

        if (now.day != 1 or now.hour != 11) and not debug:  # noqa: PLR2004
            # we only want to trigger on the first of each month
            # and also trigger at 11am
            self.logger.warning("Somehow task was started outside operational hours - %s", now)
            return

        if BSE_SERVER_ID not in [guild.id for guild in self.bot.guilds] and not debug:
            # does not support other servers yet
            self.logger.debug("%s not in guilds - not supported", BSE_SERVER_ID)
            return

        if not debug:
            self.logger.info("It's the first of the month and about ~11ish - time to trigger the awards! %s", now)
        else:
            self.logger.info("Debug is true (%s) - testing stats/awards", debug)

        # set some kind of activity here
        activity = discord.Activity(
            name="with some monthly stats and awards ",
            type=discord.ActivityType.playing,
            details="Working out monthly BSEddies awards",
        )

        if not debug:
            await self.bot.change_presence(activity=activity)

        if not debug:
            # put a "BSEBot is typing..." message
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()

        awards_builder = AwardsBuilder(self.bot, BSE_SERVER_ID, False, debug)

        self.logger.debug("Calculating stats")
        stats, message = await awards_builder.build_stats_and_message()
        self.logger.debug("Calculating awards")
        awards, bseddies_awards = await awards_builder.build_awards_and_message()

        send_messages = True
        if now.month == 1 and not debug:
            # don't send awards in Jan
            # will be superseded by the annual stuff
            send_messages = False

        self.logger.debug("Logging to DB and sending messages")
        await awards_builder.send_stats_and_awards(stats, message, awards, bseddies_awards, send_messages)

        # set activity back
        listening_activity = discord.Activity(
            name="conversations",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )

        if not debug:
            await self.bot.change_presence(activity=listening_activity)

        self.logger.info("Sent messages! Until next month!")

    @bseddies_awards.before_loop
    async def before_thread_mute(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
