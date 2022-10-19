import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID
from discordbot.statsclasses import StatsGatherer


class MonthlyBSEddiesAwards(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        
        self.stats = StatsGatherer()

        self.bseddies_awards.start()
    
    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.bseddies_awards.cancel()

    @tasks.loop(minutes=5)
    async def bseddies_awards(self):
        now = datetime.datetime.now()
        
        start, end = self.stats.get_monthly_datetime_objects()
        
        args = (BSE_SERVER_ID, start, end)
        
        guild = await self.bot.fetch_guild(BSE_SERVER_ID)
        
        # SERVER STATS
        
        num_messages = self.stats.number_of_messages(*args)
        avg_message_chars, avg_message_words = self.stats.average_message_length(*args)
        busiest_channel, busiest_channel_messages = self.stats.busiest_channel(*args)
        busiest_day, busiest_day_messages = self.stats.busiest_day(*args)
        num_bets = self.stats.number_of_bets(*args)
        
        
        busiest_channel_obj = guild.get_channel(busiest_channel)
        
        message = (
            "Some server stats from last month:\n"
            f"Number of messages sent: `{num_messages}`\n"
            f"Average message length: Characters (`{avg_message_chars}`), Words (`{avg_message_words}`)\n"
            f"Chattiest channel: {busiest_channel_obj.mention} (`{busiest_channel_messages}`)\n"
            f"Chattiest day: {busiest_day} (`{busiest_day_messages}`)"
        )
        
        
    
    @bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
