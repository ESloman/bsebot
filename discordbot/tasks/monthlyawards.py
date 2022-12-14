import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID
from discordbot.stats.awardsbuilder import AwardsBuilder


class MonthlyBSEddiesAwards(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.bseddies_awards.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.bseddies_awards.cancel()

    @tasks.loop(minutes=60)
    async def bseddies_awards(self):
        now = datetime.datetime.now()

        if not now.day == 1 or not now.hour == 11:
            # we only want to trigger on the first of each month
            # and also trigger at 11am
            return

        if BSE_SERVER_ID not in self.guilds:
            # does not support other servers yet
            return

        self.logger.info(f"It's the first of the month and about ~11ish - time to trigger the awards! {now=}")

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

        self.logger.info("Sent messages! Until next month!")

    @bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
