
import asyncio
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.tasks.basetask import BaseTask


class MonthlyBSEddiesAwards(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.bseddies_awards
        self.task.start()

    @tasks.loop(minutes=60)
    async def bseddies_awards(self):
        """
        Loop that triggers our monthly awards. This will trigger on the 1st of a month.
        Calculates guild stats/awards.
        """
        now = datetime.datetime.now()

        if not now.day == 1 or not now.hour == 11:
            # we only want to trigger on the first of each month
            # and also trigger at 11am
            return

        if BSE_SERVER_ID not in self.guild_ids:
            # does not support other servers yet
            return

        self.logger.info(f"It's the first of the month and about ~11ish - time to trigger the awards! {now=}")

        # set some kind of activity here
        activity = discord.Activity(
            name="with some monthly stats and awards ",
            type=discord.ActivityType.playing,
            details="Working out monthly BSEddies awards"
        )
        await self.bot.change_presence(activity=activity)

        # put a "BSEBot is typing..." message
        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
        await channel.trigger_typing()

        awards_builder = AwardsBuilder(self.bot, BSE_SERVER_ID, self.logger, False)

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

        self.logger.info("Sent messages! Until next month!")

    @bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
