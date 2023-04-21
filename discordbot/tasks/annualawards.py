
import asyncio
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.tasks.basetask import BaseTask


class AnnualBSEddiesAwards(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.annual_bseddies_awards
        self.task.start()

    @tasks.loop(minutes=60)
    async def annual_bseddies_awards(self):
        """
        Task that checks if we need to do the Annual BSEddies Awards.
        This should only trigger on the 1st Jan. It will do annual stats and awards.
        """
        now = datetime.datetime.now()

        if not now.day == 2 or not now.hour == 14 or not now.month == 1:
            # we only want to trigger on the first of each YEAR
            # and also trigger at 2pm
            return

        if BSE_SERVER_ID not in self.guild_ids:
            # does not support other servers yet
            return

        self.logger.info(f"Time for the annual BSEddies awards! {now=}")

        # set some kind of activity here
        activity = discord.Activity(
            name="with some annual stats and awards ",
            type=discord.ActivityType.playing,
            details="Working out annual BSEddies awards"
        )
        await self.bot.change_presence(activity=activity)

        # put a "BSEBot is typing..." message
        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
        await channel.trigger_typing()

        awards_builder = AwardsBuilder(self.bot, BSE_SERVER_ID, self.logger, True)

        self.logger.debug("Calculating stats")
        stats, message = await awards_builder.build_stats_and_message()
        self.logger.debug("Calculating awards")
        awards, bseddies_awards = await awards_builder.build_awards_and_message()

        self.logger.debug("Logging to DB and sending messages")
        await awards_builder.send_stats_and_awards(
            stats, message,
            awards, bseddies_awards
        )

        # set activity back
        listening_activity = discord.Activity(
            name="conversations",
            type=discord.ActivityType.listening,
            details="Waiting for commands!"
        )
        await self.bot.change_presence(activity=listening_activity)

        self.logger.info("Sent messages! Until next year!")

    @annual_bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
