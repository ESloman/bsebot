import datetime
from typing import List, Tuple

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import ANNUAL_AWARDS_AWARD, BSEDDIES_REVOLUTION_CHANNEL, JERK_OFF_CHAT, MONTHLY_AWARDS_PRIZE
from discordbot.statsclasses import Stat, StatsGatherer
from mongo.bsedataclasses import Awards
from mongo.bsepoints import UserPoints


class AwardsBuilder:
    def __init__(self, bot: discord.Client, guild_id: int, logger, annual=False):
        self.bot = bot
        self.guild_id = guild_id
        self.logger = logger
        self.annual = annual

        self.stats = StatsGatherer(annual)
        self.awards = Awards()
        self.user_points = UserPoints()

    async def build_stats_and_message(self) -> Tuple[List[Stat], str]:
        """
        Uses StatsGatherer to query for all the required stats
        Formats an appropriate message
        Returns all the stats object and the message

        Returns:
            Tuple[List[Stat], str]: Tuple of the list Stat objects and the stats message to send
        """

        if not self.annual:
            start, end = self.stats.get_monthly_datetime_objects()
        else:
            start, end = self.stats.get_annual_datetime_objects()

        args = (self.guild_id, start, end)

        guild = await self.bot.fetch_guild(self.guild_id)

        number_messages = self.stats.number_of_messages(*args)
        avg_message_chars, avg_message_words = self.stats.average_message_length(*args)
        busiest_channel = self.stats.busiest_channel(*args)
        busiest_day = self.stats.busiest_day(*args)
        num_bets = self.stats.number_of_bets(*args)
        salary_gains = self.stats.salary_gains(*args)
        average_wordle = self.stats.average_wordle_victory(*args)
        eddies_placed, eddies_won = self.stats.bet_eddies_stats(*args)
        most_popular_channel = self.stats.most_unique_channel_contributers(*args)

        busiest_channel_obj = await guild.fetch_channel(busiest_channel.value)
        busiest_day_format = busiest_day.value.strftime("%a %d %b")
        popular_channel_obj = await guild.fetch_channel(most_popular_channel.value)

        stats = [
            number_messages, avg_message_chars, avg_message_words, busiest_channel, busiest_day,
            num_bets, salary_gains, average_wordle, eddies_placed, eddies_won, most_popular_channel
        ]

        if not self.annual:
            message_start = (
                f"As it's the first of the month, here's some server stats 📈 from {start.strftime('%B')}:\n\n"
            )
        else:
            message_start = (
                f"As it's the first day of the year, here's some server stats 📈 from {start.strftime('%Y')}:\n\n"
            )

        message = (
            f"{message_start}"
            f"**Number of messages sent**: `{number_messages.value}` "
            f"(in `{number_messages.channels}` channels from `{number_messages.users}` users)\n"
            f"**Average message length**: Characters (`{avg_message_chars.value}`), "
            f"Words (`{avg_message_words.value}`)\n"
            f"**Chattiest channel**: {busiest_channel_obj.mention} "
            f"(`{busiest_channel.messages}` messages from `{busiest_channel.users}` users)\n"
            f"**Most popular channel**: `{popular_channel_obj.mention}` "
            f"(`{most_popular_channel.users}` unique users)\n"
            f"**Chattiest day**: {busiest_day_format} "
            f"(`{busiest_day.messages}` messages in `{busiest_day.channels}` "
            f"channels from `{busiest_day.users}` users)\n"
            f"**Average wordle score**: `{average_wordle.value}`\n"
            f"**Bets created**: `{num_bets.value}`\n"
            f"**Eddies gained via salary**: `{salary_gains.value}`\n"
            f"**Eddies placed on bets**: `{eddies_placed.value}`\n"
            f"**Eddies won on bets**: `{eddies_won.value}`\n"
        )

        return stats, message

    async def build_awards_and_message(self) -> Tuple[List[Stat], str]:
        """
        Uses StatsGatherer to gather all the awards
        Formats an awards message
        Returns the list of awards and the message

        Returns:
            Tuple[List[Stat], str]: tuple of List of Awards and the awards message
        """
        if not self.annual:
            start, end = self.stats.get_monthly_datetime_objects()
        else:
            start, end = self.stats.get_annual_datetime_objects()

        args = (self.guild_id, start, end)

        guild = await self.bot.fetch_guild(self.guild_id)

        most_messages = self.stats.most_messages_sent(*args)
        least_messages = self.stats.least_messages_sent(*args)
        longest_message = self.stats.longest_message(*args)
        best_wordle = self.stats.lowest_average_wordle_score(*args)
        most_bets = self.stats.most_bets_created(*args)
        most_eddies_placed = self.stats.most_eddies_bet(*args)
        most_eddies_won = self.stats.most_eddies_won(*args)
        longest_king = self.stats.most_time_king(*args)
        twitter_addict = self.stats.twitter_addict(*args)
        jerk_off_king = self.stats.jerk_off_contributor(*args)
        big_memer = self.stats.big_memer(*args)
        react_king = self.stats.react_king(*args)

        awards = [
            most_messages,
            least_messages,
            longest_message,
            best_wordle,
            most_bets,
            most_eddies_placed,
            most_eddies_won,
            longest_king,
            twitter_addict,
            jerk_off_king,
            big_memer,
            react_king
        ]

        user_id_dict = {}  # type: dict[int, discord.Member]
        for award in awards:
            if award.user_id in user_id_dict:
                continue
            member = await guild.fetch_member(award.user_id)
            user_id_dict[award.user_id] = member

        jerk_off_channel = await self.bot.fetch_channel(JERK_OFF_CHAT)

        if not self.annual:
            message_start = "Time for the monthly **BSEddies Awards** 🏆\n"
            prize = MONTHLY_AWARDS_PRIZE
        else:
            message_start = "Time for the _Annual_ **BSEddies Awards** 🏆\n"
            prize = ANNUAL_AWARDS_AWARD

        bseddies_awards = (
            f"{message_start}"
            f"Each award has a prize of **{prize}** eddies.\n\n"
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
            f"{user_id_dict[twitter_addict.user_id].mention} (`{twitter_addict.value}` tweets shared)\n"
            "The _'jerk off mate'_ award: "
            f"{user_id_dict[jerk_off_king.user_id].mention} "
            f"(`{jerk_off_king.value}` contributions to {jerk_off_channel.mention})\n"
            "The _'big memer'_ award: "
            f"{user_id_dict[big_memer.user_id].mention} (`{big_memer.value}` reacts received)\n"
            "The _'emoji is worth a thousand words'_ award: "
            f"{user_id_dict[react_king.user_id].mention} (`{react_king.value}` reacts given)\n"
        )

        return awards, bseddies_awards

    async def send_stats_and_awards(
        self,
        stats: List[Stat],
        stats_message: str,
        awards: List[Stat],
        awards_message: str
    ) -> None:
        """Given the stats and awards - actually log those, distribute eddies and send the message

        Args:
            stats (_type_): _description_
            stats_message (_type_): _description_
            awards (_type_): _description_
            awards_message (_type_): _description_
        """

        for stat in stats:
            # comment out this for debug
            self.awards.document_stat(**{k: v for k, v in stat.__dict__.items() if v})
            self.logger.info(f"{ {k: v for k, v in stat.__dict__.items() if v} }")

        if not self.annual:
            transaction_type = TransactionTypes.MONTHLY_AWARDS_PRIZE
        else:
            transaction_type = TransactionTypes.ANNUAL_AWARDS_PRIZE

        for award in awards:
            # comment out this for debug
            self.user_points.append_to_transaction_history(
                award.user_id,
                award.guild_id,
                {
                    "type": transaction_type,
                    "timestamp": datetime.datetime.now(),
                    "amount": award.eddies,
                }
            )
            self.user_points.increment_points(award.user_id, award.guild_id, award.eddies)
            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v})
            self.logger.info(f"{ {k: v for k, v in award.__dict__.items() if v} }")

        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)

        # uncomment for debug
        # channel = await self.bot.fetch_channel(291508460519161856)

        await channel.send(content=stats_message)
        await channel.send(content=awards_message)
