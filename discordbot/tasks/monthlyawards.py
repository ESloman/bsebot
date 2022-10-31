import datetime

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BSEDDIES_REVOLUTION_CHANNEL, BSE_SERVER_ID, MONTHLY_AWARDS_PRIZE
from discordbot.statsclasses import StatsGatherer
from mongo.bsepoints import UserPoints
from mongo.bsedataclasses import Awards


class MonthlyBSEddiesAwards(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.stats = StatsGatherer()
        self.user_points = UserPoints()
        self.awards = Awards()

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

        start, end = self.stats.get_monthly_datetime_objects()

        args = (BSE_SERVER_ID, start, end)

        guild = await self.bot.fetch_guild(BSE_SERVER_ID)

        # SERVER STATS
        # get all generic discord server stats

        number_messages = self.stats.number_of_messages(*args)
        avg_message_chars, avg_message_words = self.stats.average_message_length(*args)
        busiest_channel = self.stats.busiest_channel(*args)
        busiest_day = self.stats.busiest_day(*args)
        num_bets = self.stats.number_of_bets(*args)
        salary_gains = self.stats.salary_gains(*args)
        average_wordle = self.stats.average_wordle_victory(*args)
        eddies_placed, eddies_won = self.stats.bet_eddies_stats(*args)

        busiest_channel_obj = await guild.fetch_channel(busiest_channel.value)
        busiest_day_format = busiest_day.value.strftime("%a %d %b")

        stats = [
            number_messages, avg_message_chars, avg_message_words, busiest_channel, busiest_day
        ]

        message = (
            "Some server stats 📈 from last month:\n\n"
            f"**Number of messages sent**: `{number_messages.value}`\n"
            f"**Average message length**: Characters (`{avg_message_chars.value}`), "
            f"Words (`{avg_message_words.value}`)\n"
            f"**Chattiest channel**: {busiest_channel_obj.mention} (`{busiest_channel.messages}`)\n"
            f"**Chattiest day**: {busiest_day_format} (`{busiest_day.messages}`)\n"
            f"**Average wordle score**: `{average_wordle.value}`\n"
            f"**Bets created**: `{num_bets.value}`\n"
            f"**Eddies gained via salary**: `{salary_gains.value}`\n"
            f"**Eddies placed on bets**: `{eddies_placed.value}`\n"
            f"**Eddies won on bets**: `{eddies_won.value}`\n"
        )

        for stat in stats:
            self.awards.document_stat(**{k: v for k, v in stat.__dict__.items() if v})
            self.logger.info(f"{ {k: v for k, v in stat.__dict__.items() if v} }")

        # BSEDDIES AWARDS
        # get all stats for bseddies awards

        most_messages = self.stats.most_messages_sent(*args)
        least_messages = self.stats.least_messages_sent(*args)
        longest_message = self.stats.longest_message(*args)
        best_wordle = self.stats.lowest_average_wordle_score(*args)
        most_bets = self.stats.most_bets_created(*args)
        most_eddies_placed = self.stats.most_eddies_bet(*args)
        most_eddies_won = self.stats.most_eddies_won(*args)
        longest_king = self.stats.most_time_king(*args)
        twitter_addict = self.stats.twitter_addict(*args)

        awards = [
            most_messages,
            least_messages,
            longest_message,
            best_wordle,
            most_bets,
            most_eddies_placed,
            most_eddies_won,
            longest_king,
            twitter_addict
        ]

        user_id_dict = {}  # type: dict[int, discord.Member]
        for award in awards:
            if award.user_id in user_id_dict:
                continue
            member = await guild.fetch_member(award.user_id)
            user_id_dict[award.user_id] = member

        bseddies_awards = (
            "Time for the monthly **BSEddies Awards** 🏆\n"
            f"Each award has a prize of **{MONTHLY_AWARDS_PRIZE}** eddies.\n\n"
            "The _'won't shut up'_ award: "
            f"{user_id_dict[most_messages.user_id].mention} (`{most_messages.value}` messages sent)\n"
            "The _'can't find the enter key'_ award: "
            f"{user_id_dict[longest_message.user_id].mention} (`{longest_message.value}` longest message length)\n"
            "The _'I have an English degree'_ award: "
            f"{user_id_dict[best_wordle.user_id].mention} (`{best_wordle.value}` average wordle score)\n"
            "The _'bookie'_ award: "
            f"{user_id_dict[most_bets.user_id].mention} (`{most_bets.value}` bets created)\n"
            "The _'just one more bet'_ award: "
            f"{user_id_dict[most_eddies_placed.user_id].mention} (`{most_eddies_placed.value}` eddies bet)\n"
            "The _'rollin' in it'_ award: "
            f"{user_id_dict[most_eddies_won.user_id].mention} (`{most_eddies_won.value}` eddies won)\n"
            "The _'king of kings'_ award: "
            f"{user_id_dict[longest_king.user_id].mention} "
            f"(`{str(datetime.timedelta(seconds=longest_king.value))}` spent as KING)\n"
            "The _'participation'_ award: "
            f"{user_id_dict[least_messages.user_id].mention} (`{least_messages.value}` messages sent)\n"
            "The _'twitter addict'_ award: "
            f"{user_id_dict[twitter_addict.user_id].mention} (`{twitter_addict.value}` tweets shared)"
        )

        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)

        await channel.send(content=message)
        await channel.send(content=bseddies_awards)

        # give the users their eddies

        for award in awards:
            self.user_points.append_to_transaction_history(
               award.user_id,
               award.guild_id,
               {
                   "type": TransactionTypes.MONTHLY_AWARDS_PRIZE,
                   "timestamp": datetime.datetime.now(),
                   "amount": award.eddies,
               }
            )
            self.user_points.increment_points(award.user_id, award.guild_id, award.eddies)
            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v})
            self.logger.info(f"{ {k: v for k, v in award.__dict__.items() if v} }")

        self.logger.info("Sent messages! Until next month!")

    @bseddies_awards.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
