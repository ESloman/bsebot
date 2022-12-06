import datetime
from typing import List, Tuple

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import ANNUAL_AWARDS_AWARD, BSEDDIES_REVOLUTION_CHANNEL, JERK_OFF_CHAT, MONTHLY_AWARDS_PRIZE
from discordbot.stats.statsclasses import Stat, StatsGatherer
from mongo.bsedataclasses import Awards
from mongo.bsepoints import UserPoints


class AwardsBuilder:
    def __init__(self, bot: discord.Client, guild_id: int, logger, annual=False):
        self.bot = bot
        self.guild_id = guild_id
        self.logger = logger
        self.annual = annual

        self.stats = StatsGatherer(logger, annual)
        self.awards = Awards()
        self.user_points = UserPoints()

    async def build_stats_and_message(self) -> Tuple[List[Stat], List[str]]:
        """
        Uses StatsGatherer to query for all the required stats
        Formats an appropriate message
        Returns all the stats object and the message

        Returns:
            Tuple[List[Stat], List[str]]: Tuple of the list Stat objects and the stats message to send
        """

        if not self.annual:
            start, end = self.stats.get_monthly_datetime_objects()
        else:
            start, end = self.stats.get_annual_datetime_objects()

        args = (self.guild_id, start, end)

        guild = await self.bot.fetch_guild(self.guild_id)

        # get a list of channel IDs here to use
        _channels = await guild.fetch_channels()
        _channels = [c for c in _channels if c.type in [discord.ChannelType.text, discord.ChannelType.private]]
        _channel_ids = [c.id for c in _channels]

        number_messages = self.stats.number_of_messages(*args)
        avg_message_chars, avg_message_words = self.stats.average_message_length(*args)
        busiest_channel = self.stats.busiest_channel(*args)
        busiest_thread = self.stats.busiest_thread(*args)
        busiest_day = self.stats.busiest_day(*args)
        num_bets = self.stats.number_of_bets(*args)
        salary_gains = self.stats.salary_gains(*args)
        average_wordle = self.stats.average_wordle_victory(*args)
        eddies_placed, eddies_won = self.stats.bet_eddies_stats(*args)
        most_popular_channel = self.stats.most_unique_channel_contributers(*args)
        time_spent_in_vc = self.stats.total_time_spent_in_vc(*args)
        vc_most_time_spent = self.stats.vc_with_most_time_spent(*args)
        vc_most_users = self.stats.vc_with_most_users(*args)
        most_used_server_emoji = self.stats.most_popular_server_emoji(*args)
        threads_created = self.stats.threads_created(*args)
        thread_messages = self.stats.number_of_threaded_messages(*args)
        quietest_channel = self.stats.quietest_channel(*args, _channel_ids)
        quietest_thread = self.stats.quietest_thread(*args)
        quietest_day = self.stats.quietest_day(*args)
        emojis_created = self.stats.emojis_created(*args)

        busiest_channel_obj = await guild.fetch_channel(busiest_channel.value)
        quietest_channel_obj = await guild.fetch_channel(quietest_channel.value)
        busiest_thread_obj = await guild.fetch_channel(busiest_thread.value)
        quietest_thread_obj = await guild.fetch_channel(quietest_thread.value)
        busiest_day_format = busiest_day.value.strftime("%a %d %b")
        quietest_day_format = quietest_day.value.strftime("%a %d %b")
        popular_channel_obj = await guild.fetch_channel(most_popular_channel.value)
        vc_time_obj = await guild.fetch_channel(vc_most_time_spent.value)
        vc_users_obj = await guild.fetch_channel(vc_most_users.value)
        emoji_obj = await guild.fetch_emoji(most_used_server_emoji.emoji_id)

        thread_objects = [
            await guild.fetch_channel(thread_id) for thread_id in threads_created.threads
        ]

        emoji_objects = [
            await guild.fetch_emoji(emoji_id) for emoji_id in emojis_created.emoji_ids
        ]

        stats = [
            number_messages, avg_message_chars, avg_message_words, busiest_channel, busiest_day,
            num_bets, salary_gains, average_wordle, eddies_placed, eddies_won, most_popular_channel,
            time_spent_in_vc, vc_most_time_spent, vc_most_users, most_used_server_emoji, busiest_thread,
            threads_created, thread_messages, quietest_day, quietest_channel, quietest_thread
        ]

        if not self.annual:
            message_start = (
                f"As it's the first of the month, here's some server stats 📈 from {start.strftime('%B')}:\n\n"
            )
        else:
            message_start = (
                f"As it's the first day of the year, here's some server stats 📈 from {start.strftime('%Y')}:\n"
                "_(Voice stats 🎤 from Nov 22 onwards)_\n\n"
            )

        if busiest_thread_obj.archived:
            b_thread_text = f"`#{busiest_thread_obj.name} (archived)`"
        else:
            b_thread_text = busiest_thread_obj.mention

        if quietest_thread_obj.archived:
            q_thread_text = f"`#{quietest_thread_obj.name} (archived)`"
        else:
            q_thread_text = quietest_thread_obj.mention

        stat_parts = [
            message_start,
            (f"**Number of messages sent** 📬: `{number_messages.value}` "
             f"(in `{number_messages.channels}` channels from `{number_messages.users}` users)\n"),
            (f"**Number of thread messages sent** 📟: `{thread_messages.value}` "
             f"(in `{thread_messages.channels}` thread from `{thread_messages.users}` users)\n"),
            (f"**Average message length** 📰: Characters (`{avg_message_chars.value}`), "
             f"Words (`{avg_message_words.value}`)\n"),
            (f"**Chattiest channel** 🖨️: {busiest_channel_obj.mention} "
             f"(`{busiest_channel.messages}` messages from `{busiest_channel.users}` users)\n"),
            (f"**Quietest channel** 📭: {quietest_channel_obj.mention} "
             f"(`{quietest_channel.messages}` messages from `{quietest_channel.users}` users)\n"),
            (f"**Chattiest thread** 📧: {b_thread_text} "
             f"(`{busiest_thread.messages}` messages from `{busiest_thread.users}` users)\n"),
            (f"**Quietest thread** 📖: {q_thread_text} "
             f"(`{quietest_thread.messages}` messages from `{quietest_thread.users}` users)\n"),
            (f"**Most popular channel** 💌: {popular_channel_obj.mention} "
             f"(`{most_popular_channel.users}` unique users)\n"),
            (f"**Threads created** 🖇️: {threads_created.value} "
             f"({','.join([t.mention for t in thread_objects]) if len(thread_objects) < 5 else '_too many to list_'})"
             "\n"),
            (f"**Chattiest day** 🗓️: {busiest_day_format} "
             f"(`{busiest_day.messages}` messages in `{busiest_day.channels}` "
             f"channels from `{busiest_day.users}` users)\n"),
            (f"**Quietest day** 📆: {quietest_day_format} "
             f"(`{quietest_day.messages}` messages in `{quietest_day.channels}` "
             f"channels from `{quietest_day.users}` users)\n"),
            (f"**Average wordle score** 🟩: `{average_wordle.value}`\n"),
            (f"**Total time spent in VCs** 📱: `{str(datetime.timedelta(seconds=time_spent_in_vc.value))}` "
             f"(`in {time_spent_in_vc.channels}` channels from `{time_spent_in_vc.users}` users)\n"),
            (f"**Talkiest VC** 💬: {vc_time_obj.mention} (`{vc_most_time_spent.users}` users spent "
             f"`{str(datetime.timedelta(seconds=vc_most_time_spent.time))}` in this VC)\n"),
            (f"**Most popular VC** 🎉: {vc_users_obj.mention} (`{vc_most_users.users}` unique users spent "
             f"`{str(datetime.timedelta(seconds=vc_most_users.time))}` in this VC)\n"),
            (f"**Bets created** 🗃️: `{num_bets.value}`\n"),
            (f"**Eddies gained via salary** 👩🏼‍💼: `{salary_gains.value}`\n"),
            (f"**Eddies placed on bets** 🧑🏼‍💻: `{eddies_placed.value}`\n"),
            (f"**Eddies won on bets** 🧑🏼‍🏫: `{eddies_won.value}`\n"),
            (f"**Most popular server emoji** 🗳️: {emoji_obj} (`{most_used_server_emoji.count}`)"),
        ]

        if self.annual:
            stat_parts.append(
                (f"\n**Emojis created** : {emojis_created.value} "
                 f"({', '.join([str(e) for e in emoji_objects])})")
            )

        bseddies_stats = []
        message = ""
        for msg_part in stat_parts:
            if len(message + msg_part) > 1980:
                bseddies_stats.append(message)
                message = ""
            message += msg_part
        bseddies_stats.append(message)

        return stats, bseddies_stats

    async def build_awards_and_message(self) -> Tuple[List[Stat], List[str]]:
        """
        Uses StatsGatherer to gather all the awards
        Formats an awards message
        Returns the list of awards and the message

        Returns:
            Tuple[List[Stat], List[str]]: tuple of List of Awards and the awards messages
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
        big_gamer = self.stats.big_gamer(*args)
        big_streamer = self.stats.big_streamer(*args)
        threadiest_user = self.stats.most_thread_messages_sent(*args)
        serial_replier, conversation_starter = self.stats.most_replies(*args)
        owner_award = self.stats.server_owner(guild, start)
        fattest_fingers = self.stats.most_edited_messages(*args)

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
            react_king,
            big_gamer,
            big_streamer,
            threadiest_user,
            serial_replier,
            conversation_starter,
            owner_award,
            fattest_fingers
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
            message_start = (
                "Time for the _Annual_ **BSEddies Awards** 🏆\n"
                "_(Voice awards 🎤 from Nov 22 onwards)_\n"
            )
            prize = ANNUAL_AWARDS_AWARD

        awards_parts = [
            message_start,
            f"Each award has a prize of **{prize}** eddies.\n\n",
            # most messages
            ("The _'won't shut up'_ 🤐 award: "
             f"{user_id_dict[most_messages.user_id].mention} (`{most_messages.value}` messages sent)\n"),
            # the longest message
            ("The _'can't find the enter key'_ ⌨️ award: "
             f"{user_id_dict[longest_message.user_id].mention} (`{longest_message.value}` longest message length)\n"),
            # most messages to a thread
            ("The _'best threads'_ 🧵 award: "
             f"{user_id_dict[threadiest_user.user_id].mention} (`{threadiest_user.value}` messages sent to threads)\n"),
            # best wordle score
            ("The _'I have an English degree'_ 📑 award: "
             f"{user_id_dict[best_wordle.user_id].mention} (`{best_wordle.value}` average wordle score)\n"),
            # the least messages sent
            ("The _'participation'_ 🥉 award: "
             f"{user_id_dict[least_messages.user_id].mention} (`{least_messages.value}` messages sent)\n"),
            # most replies
            ("The _'serial replier'_ 📝 award: "
             f"{user_id_dict[serial_replier.user_id].mention} (`{serial_replier.value}` replies)\n"),
            # most replied to
            ("The _'conversation started'_ 📥 award: "
             f"{user_id_dict[conversation_starter.user_id].mention} "
             f"(`{conversation_starter.value}` replies _received_)\n"),
            # twitter links
            ("The _'twitter addict'_ 🐦 award: "
             f"{user_id_dict[twitter_addict.user_id].mention} (`{twitter_addict.value}` tweets shared)\n"),
            # jerk-off-chat contribs
            ("The _'jerk off mate'_ 🍆 award: "
             f"{user_id_dict[jerk_off_king.user_id].mention} "
             f"(`{jerk_off_king.value}` contributions to {jerk_off_channel.mention})\n"),
            # most reacts
            ("The _'big memer'_ 😎 award: "
             f"{user_id_dict[big_memer.user_id].mention} (`{big_memer.value}` reacts received)\n"),
            # most reacts given
            ("The _'emoji is worth a thousand words'_ 😂 award: "
             f"{user_id_dict[react_king.user_id].mention} (`{react_king.value}` reacts given)\n"),
            # most time spent in VC
            ("The _'big talker'_ 🔊 award: "
             f"{user_id_dict[big_gamer.user_id].mention} "
             f"(`{str(datetime.timedelta(seconds=big_gamer.value))}` spent in {big_gamer.channels} channels)\n"),
            # most time streaming
            ("The _'wannabe streamer'_ 🖥️ award: "
             f"{user_id_dict[big_streamer.user_id].mention} (`{str(datetime.timedelta(seconds=big_streamer.value))}` "
             f"spent streaming in {big_streamer.channels} channels)\n"),
            # most bets created
            ("The _'bookie'_ 🤑 award: "
             f"{user_id_dict[most_bets.user_id].mention} (`{most_bets.value}` bets created)\n"),
            # most eddies bet
            ("The _'just one more bet'_ 💵 award: "
             f"{user_id_dict[most_eddies_placed.user_id].mention} (`{most_eddies_placed.value}` eddies bet)\n"),
            # most eddies won
            ("The _'rollin' in it'_ 💰 award: "
             f"{user_id_dict[most_eddies_won.user_id].mention} (`{most_eddies_won.value}` eddies won)\n"),
            # most time king
            ("The _'king of kings'_ 👑 award: "
             f"{user_id_dict[longest_king.user_id].mention} "
             f"(`{str(datetime.timedelta(seconds=longest_king.value))}` spent as KING)\n"),
            # server owner award
            ("The _'server owner'_ 👨‍👧‍👦 award: "
             f"{user_id_dict[owner_award.user_id].mention}\n"),
            # edited messages
            ("The _'fat fingers'_ 🖐🏼 award: "
             f"{user_id_dict[fattest_fingers.user_id].mention} (`{fattest_fingers.value}` edits to "
             f"`{fattest_fingers.message_count}` messages)")
        ]

        bseddies_awards = []

        message = ""
        for msg_part in awards_parts:
            if len(message + msg_part) > 1980:
                bseddies_awards.append(message)
                message = ""
            message += msg_part
        bseddies_awards.append(message)

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
            self.awards.document_stat(**{k: v for k, v in stat.__dict__.items() if v is not None})
            self.logger.info(f"{ {k: v for k, v in stat.__dict__.items() if v is not None} }")

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
            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v is not None})
            self.logger.info(f"{ {k: v for k, v in award.__dict__.items() if v is not None} }")

        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)

        # uncomment for debug
        # channel = await self.bot.fetch_channel(291508460519161856)

        self.logger.info(f"Stats message is {len(awards_message)} messages long")
        for message in stats_message:
            self.logger.info(f"Stats message part is {len(message)} chars long")
            await channel.send(content=message)

        self.logger.info(f"Awards message is {len(awards_message)} messages long")
        for message in awards_message:
            self.logger.info(f"Awards message part is {len(message)} chars long")
            await channel.send(content=message)
