import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID
from discordbot.stats.awardsbuilder import AwardsBuilder


class AnnualBSEddiesAwards(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds

        self.annual_bseddies_awards.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.annual_bseddies_awards.cancel()

    @tasks.loop(minutes=60)
    async def annual_bseddies_awards(self):
        now = datetime.datetime.now()

        if not now.day == 2 or not now.hour == 14 or not now.month == 1:
            # we only want to trigger on the first of each YEAR
            # and also trigger at 2pm
            return

        if BSE_SERVER_ID not in self.guilds:
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
        :return:
        """
        await self.bot.wait_until_ready()
