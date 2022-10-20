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
        salary_gains = self.stats.salary_gains(*args)
        average_wordle = self.stats.average_wordle_victory(*args)
        eddies_placed, eddies_won = self.stats.bet_eddies_stats(*args)

        busiest_channel_obj = await guild.fetch_channel(busiest_channel)
        busiest_day_format = busiest_day.strftime("%a %d %b")
        
        message = (
            "Some server stats 📈 from last month:\n\n"
            f"**Number of messages sent**: `{num_messages}`\n"
            f"**Average message length**: Characters (`{avg_message_chars}`), Words (`{avg_message_words}`)\n"
            f"**Chattiest channel**: {busiest_channel_obj.mention} (`{busiest_channel_messages}`)\n"
            f"**Chattiest day**: {busiest_day_format} (`{busiest_day_messages}`)\n"
            f"**Average wordle score**: `{average_wordle}`\n"
            f"**Bets created**: `{num_bets}`\n"
            f"**Eddies gained via salary**: `{salary_gains}`\n"
            f"**Eddies placed on bets**: `{eddies_placed}`\n"
            f"**Eddies won on bets**: `{eddies_won}`\n"
        )

        # BSEDDIES AWARDS

        most_messages_id, most_messages_count = self.stats.most_messages_sent(*args)
        longest_message_id, longest_message_count = self.stats.longest_message(*args)
        wordle_id, wordle_avg_score = self.stats.lowest_average_wordle_score(*args)
        most_bets_id, most_bets_number = self.stats.most_bets_created(*args)
        most_eddies_placed_id, most_eddies_placed = self.stats.most_eddies_bet(*args)
        most_eddies_won_id, most_eddies_won = self.stats.most_eddies_won(*args)

        user_id_dict = {}  # type: dict[int, discord.Member]
        for _id in [
            most_messages_id, longest_message_id, wordle_id,
            most_bets_id, most_eddies_placed_id, most_eddies_won_id
        ]:
            if _id in user_id_dict:
                continue
            member = await guild.fetch_member(_id)
            user_id_dict[_id] = member

        bseddies_awards = (
            "Time for the monthly **BSEddies Awards** 🏆\n\n"
            "The _'won't shut up'_ award: "
            f"{user_id_dict[most_messages_id].mention} (`{most_messages_count}` messages sent)\n"
            "The _'can't find the enter key'_ award: "
            f"{user_id_dict[longest_message_id].mention} (`{longest_message_count}` longest message length)\n"
            "The _'I have an English degree'_ award: "
            f"{user_id_dict[wordle_id].mention} (`{wordle_avg_score}` average wordle score)\n"
            "The _'bookie'_ award: "
            f"{user_id_dict[most_bets_id].mention} (`{most_bets_number}` bets created)\n"
            "The _'just one more bet'__ award: "
            f"{user_id_dict[most_eddies_placed_id].mention} (`{most_eddies_placed}` eddies bet)\n"
            "The _'rollin' in it'_ award: "
            f"{user_id_dict[most_eddies_won_id].mention} (`{most_eddies_won}` eddies won)\n"
        )

        # TESTING ONLY
        sloman_guild = await self.bot.fetch_guild(291508460519161856)
        sloman_channel = await self.bot.fetch_channel(291508460519161856)

        self.logger.info(message)
        self.logger.info(bseddies_awards)

        await sloman_channel.send(content=message)
        await sloman_channel.send(content=bseddies_awards)


    @bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
