import datetime
from typing import List, Tuple

import discord

from discordbot.bsebot import BSEBot
from discordbot.bot_enums import TransactionTypes
from discordbot.constants import ANNUAL_AWARDS_AWARD, BSEDDIES_REVOLUTION_CHANNEL, JERK_OFF_CHAT, MONTHLY_AWARDS_PRIZE
from discordbot.stats.statsclasses import Stat, StatsGatherer
from mongo.bsedataclasses import Awards
from mongo.bsepoints.points import UserPoints


class AwardsBuilder:
    def __init__(self, bot: BSEBot, guild_id: int, logger, annual=False):
        self.bot = bot
        self.guild_id = guild_id
        self.logger = logger
        self.annual = annual

        self.stats = StatsGatherer(logger, annual)
        self.awards = Awards()
        self.user_points = UserPoints()

    def _get_previous_stat(self, stat: Stat) -> dict:
        """
        Searches the database for the previous stat of the same time

        Args:
            stat (Stat): the stat to get previous values for

        Returns:
            dict: the previous stat object
        """
        query = {
            "guild_id": stat.guild_id,
            "type": stat.type,
            "stat": stat.stat
        }

        if stat.annual:
            query["year"] = int(stat.year) - 1
        else:
            query["month"] = (stat.timestamp - datetime.timedelta(days=7)).strftime("%b %y")

        ret = self.awards.query(query)
        return ret

    def _get_comparison_string(self, new_value: float | int, old_value: float | int) -> str:
        """
        Creates a basic comparison string we can use in stats text

        Args:
            new_value (float | int): the incumbent stat value
            old_value (float | int): the previous stat value

        Returns:
            str: a formatted string
        """
        diff = new_value - old_value

        perc = round((diff / old_value) * 100, 2)

        if perc < 0:
            # make percentage positive
            perc *= -1

        _string = f" ({'up' if diff > 0 else 'down'} `{perc}%`)"

        if diff == 0:
            _string = " (no change)"

        return _string

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

        self.logger.info(f"Got start/end to be: {start}, {end}")

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

        busiest_thread_obj = await self.bot.fetch_channel(busiest_thread.value)
        quietest_thread_obj = await self.bot.fetch_channel(quietest_thread.value)
        busiest_day_format = busiest_day.value.strftime("%a %d %b")
        quietest_day_format = quietest_day.value.strftime("%a %d %b")
        popular_channel_obj = await self.bot.fetch_channel(most_popular_channel.value)
        vc_time_obj = await self.bot.fetch_channel(vc_most_time_spent.value)
        vc_users_obj = await self.bot.fetch_channel(vc_most_users.value)
        emoji_obj = await guild.fetch_emoji(most_used_server_emoji.emoji_id)

        thread_objects = [
            await self.bot.fetch_channel(thread_id) for thread_id in threads_created.threads
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
                f"{start.strftime('%B')} server stats 📈:\n\n"
            )
        else:
            message_start = (
                f"{start.strftime('%Y')} server stats 📈:\n\n"
            )

        if busiest_thread_obj.archived:
            b_thread_text = f"`#{busiest_thread_obj.name} (archived)`"
        else:
            b_thread_text = busiest_thread_obj.mention

        if quietest_thread_obj.archived:
            q_thread_text = f"`#{quietest_thread_obj.name} (archived)`"
        else:
            q_thread_text = quietest_thread_obj.mention

        comparisons = {}
        # stats we can compare
        for stat in [
            number_messages, thread_messages, avg_message_words, avg_message_chars,
            num_bets, salary_gains, average_wordle, eddies_placed, eddies_won,
            time_spent_in_vc
        ]:
            try:
                previous = self._get_previous_stat(stat)

                if not previous:
                    comparisons[stat.stat] = ""
                    continue

                comparison_string = self._get_comparison_string(stat.value, previous["value"])
            except Exception as e:
                self.logger.debug(f"Got {e} working out {stat.short_name} comparison string")
                comparisons[stat.stat] = ""
                continue

            comparisons[stat.stat] = comparison_string

        # this is a mess
        stat_parts = [
            message_start,
            (f"- **Number of messages sent** 📬: `{number_messages.value}` "
             f"(in `{number_messages.channels}` channel{'s' if thread_messages.channels != 1 else ''} "
             f"from `{number_messages.users}` users){comparisons.get(number_messages.stat)}\n"),
            (f"- **Number of thread messages sent** 📟: `{thread_messages.value}` "
             f"(in `{thread_messages.channels}` thread{'s' if thread_messages.channels != 1 else ''} "
             f"from `{thread_messages.users}` users){comparisons.get(thread_messages.stat)}\n"),
            (f"- **Average message length** 📰: Characters (`{avg_message_chars.value}`), "
             f"Words (`{avg_message_words.value}`)\n"),
            (f"- **Chattiest channel** 🖨️: <#{busiest_channel.value}> "
             f"(`{busiest_channel.messages}` messages from `{busiest_channel.users}` users)\n"),
            (f"- **Quietest channel** 📭: <#{quietest_channel.value}> "
             f"(`{quietest_channel.messages}` messages from `{quietest_channel.users}` users)\n"),
            (f"- **Chattiest thread** 📧: {b_thread_text} "
             f"(`{busiest_thread.messages}` messages from `{busiest_thread.users}` users)\n"),
            (f"- **Quietest thread** 📖: {q_thread_text} "
             f"(`{quietest_thread.messages}` messages from `{quietest_thread.users}` users)\n"),
            (f"- **Most popular channel** 💌: {popular_channel_obj.mention} "
             f"(`{most_popular_channel.users}` unique users)\n"),
            (f"- **Threads created** 🖇️: {threads_created.value} "
             f"({','.join([t.mention for t in thread_objects]) if len(thread_objects) < 5 else '_too many to list_'})"
             "\n"),
            (f"- **Chattiest day** 🗓️: {busiest_day_format} "
             f"(`{busiest_day.messages}` messages in `{busiest_day.channels}` "
             f"channels from `{busiest_day.users}` users)\n"),
            (f"- **Quietest day** 📆: {quietest_day_format} "
             f"(`{quietest_day.messages}` messages in `{quietest_day.channels}` "
             f"channels from `{quietest_day.users}` users)\n"),
            (f"- **Average wordle score** 🟩: `{average_wordle.value}` "
             f"(the bot's: `{average_wordle.bot_average}`){comparisons.get(average_wordle.stat)}\n"),
            (f"- **Total time spent in VCs** 📱: `{str(datetime.timedelta(seconds=time_spent_in_vc.value))}` "
             f"(`in {time_spent_in_vc.channels}` channels from `{time_spent_in_vc.users}` users)"
             f"{comparisons.get(time_spent_in_vc.stat)}\n"),
            (f"- **Talkiest VC** 💬: {vc_time_obj.mention} (`{vc_most_time_spent.users}` users spent "
             f"`{str(datetime.timedelta(seconds=vc_most_time_spent.time))}` in this VC)\n"),
            (f"- **Most popular VC** 🎉: {vc_users_obj.mention} (`{vc_most_users.users}` unique users spent "
             f"`{str(datetime.timedelta(seconds=vc_most_users.time))}` in this VC)\n"),
            (f"- **Bets created** 🗃️: `{num_bets.value}`{comparisons.get(num_bets.stat)}\n"),
            (f"- **Eddies gained via salary** 👩🏼‍💼: `{salary_gains.value}`{comparisons.get(salary_gains.stat)}\n"),
            (f"- **Eddies placed on bets** 🧑🏼‍💻: `{eddies_placed.value}`{comparisons.get(eddies_placed.stat)}\n"),
            (f"- **Eddies won on bets** 🧑🏼‍🏫: `{eddies_won.value}`{comparisons.get(eddies_won.stat)}\n"),
            (f"- **Most popular server emoji** 🗳️: {emoji_obj} (`{most_used_server_emoji.count}`)"),
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

        self.logger.info(f"Got start/end to be: {start}, {end}")

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
        most_swears = self.stats.most_swears(*args)
        single_minded = self.stats.most_messages_to_a_single_channel(*args)
        diverse_portfolio = self.stats.most_messages_to_most_channels(*args)

        awards = [
            most_messages, least_messages, longest_message, best_wordle, most_bets,
            most_eddies_placed, most_eddies_won, longest_king, twitter_addict, jerk_off_king,
            big_memer, react_king, big_gamer, big_streamer, threadiest_user,
            serial_replier, conversation_starter, owner_award, fattest_fingers,
            most_swears, single_minded, diverse_portfolio
        ]

        if not self.annual:
            message_start = f"# {start.strftime('%B')} BSEddies Awards 🏆\n"
            prize = MONTHLY_AWARDS_PRIZE
        else:
            message_start = (
                f"# {start.strftime('%Y')} BSEddies Awards 🏆\n\n"
            )
            prize = ANNUAL_AWARDS_AWARD

        awards_parts = [
            message_start,
            f"### Each award has a prize of **{prize}** eddies.\n\n",
            # server owner award
            ("- The _'server owner'_ 👨‍👧‍👦 award: "
             f"<@!{owner_award.user_id}>\n"),
            # most messages
            ("- The _'won't shut up'_ 🤐 award: "
             f"<@!{most_messages.user_id}> (`{most_messages.value}` messages sent)\n"),
            # the longest message
            ("- The _'can't find the enter key'_ ⌨️ award: "
             f"<@!{longest_message.user_id}> (`{longest_message.value}` longest message length)\n"),
            # most messages to a thread
            ("- The _'best threads'_ 🧵 award: "
             f"<@!{threadiest_user.user_id}> (`{threadiest_user.value}` messages sent to threads)\n"),
            # the least messages sent
            ("- The _'participation'_ 🥉 award: "
             f"<@!{least_messages.user_id}> (`{least_messages.value}` messages sent)\n"),
            # single minded
            ("- The _'single minded'_ 🧠 award: "
             f"<@!{single_minded.user_id}> (`{single_minded.value}%` of messages "
             f"sent to <#{single_minded.channel}>)\n"),
            # diverse portfolio
            ("- The _'diverse portfolio'_ 💼 award: "
             f"<@!{diverse_portfolio.user_id}> (`{diverse_portfolio.messages}` sent to "
             f"`{diverse_portfolio.value}` channels)\n"),
            # most replies
            ("- The _'serial replier'_ 📝 award: "
             f"<@!{serial_replier.user_id}> (`{serial_replier.value}` replies)\n"),
            # most replied to
            ("- The _'conversation started'_ 📥 award: "
             f"<@!{conversation_starter.user_id}> "
             f"(`{conversation_starter.value}` replies _received_)\n"),
            # twitter links
            ("- The _'twitter addict'_ 🐦 award: "
             f"<@!{twitter_addict.user_id}> (`{twitter_addict.value}` tweets shared)\n"),
            # jerk-off-chat contribs
            ("- The _'jerk off mate'_ 🍆 award: "
             f"<@!{jerk_off_king.user_id}> "
             f"(`{jerk_off_king.value}` contributions to <#{JERK_OFF_CHAT}>)\n"),
            # edited messages
            ("- The _'fat fingers'_ 🖐🏼 award: "
             f"<@!{fattest_fingers.user_id}> (`{fattest_fingers.value}` edits to "
             f"`{fattest_fingers.message_count}` messages)\n"),
            # most swears
            ("- The _'dirtiest fingers'_ 🚽 award: "
             f"<@!{most_swears.user_id}> (`{most_swears.value}` swears)\n"),
            # best wordle score
            ("- The _'I have an English degree'_ 📑 award: "
             f"<@!{best_wordle.user_id}> (`{best_wordle.value}` average wordle score)\n"),
            # most reacts
            ("- The _'big memer'_ 😎 award: "
             f"<@!{big_memer.user_id}> (`{big_memer.value}` reacts received)\n"),
            # most reacts given
            ("- The _'emoji is worth a thousand words'_ 😂 award: "
             f"<@!{react_king.user_id}> (`{react_king.value}` reacts given)\n"),
            # most time spent in VC
            ("- The _'big talker'_ 🔊 award: "
             f"<@!{big_gamer.user_id}> "
             f"(`{str(datetime.timedelta(seconds=big_gamer.value))}` spent in {big_gamer.channels} channels)\n"),
            # most time streaming
            ("- The _'wannabe streamer'_ 🖥️ award: "
             f"<@!{big_streamer.user_id}> (`{str(datetime.timedelta(seconds=big_streamer.value))}` "
             f"spent streaming in {big_streamer.channels} channels)\n"),
            # most bets created
            ("- The _'bookie'_ 🤑 award: "
             f"<@!{most_bets.user_id}> (`{most_bets.value}` bets created)\n"),
            # most eddies bet
            ("- The _'just one more bet'_ 💵 award: "
             f"<@!{most_eddies_placed.user_id}> (`{most_eddies_placed.value}` eddies bet)\n"),
            # most eddies won
            ("- The _'rollin' in it'_ 💰 award: "
             f"<@!{most_eddies_won.user_id}> (`{most_eddies_won.value}` eddies won)\n"),
            # most time king
            ("- The _'king of kings'_ 👑 award: "
             f"<@!{longest_king.user_id}> "
             f"(`{str(datetime.timedelta(seconds=longest_king.value))}` spent as KING)"),
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
            self.user_points.increment_points(
                award.user_id,
                award.guild_id,
                award.eddies,
                transaction_type,
                award_name=award.short_name
            )
            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v is not None})
            self.logger.info(f"{ {k: v for k, v in award.__dict__.items() if v is not None} }")

        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)

        # uncomment for debug
        # channel = await self.bot.fetch_channel(291508460519161856)

        self.logger.info(f"Stats message is {len(awards_message)} messages long")
        for message in stats_message:
            self.logger.info(f"Stats message part is {len(message)} chars long")
            await channel.send(content=message, silent=True)

        self.logger.info(f"Awards message is {len(awards_message)} messages long")
        for message in awards_message:
            self.logger.info(f"Awards message part is {len(message)} chars long")
            await channel.send(content=message, silent=True)
