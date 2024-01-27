"""Our Awards Builder class."""

import datetime
from logging import Logger

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.constants import (
    ANNUAL_AWARDS_AWARD,
    BSE_BOT_ID,
    BSEDDIES_REVOLUTION_CHANNEL,
    JERK_OFF_CHAT,
    MONTHLY_AWARDS_PRIZE,
    SLOMAN_SERVER_ID,
)
from discordbot.stats.statsclasses import StatDB, StatsGatherer
from mongo.bsedataclasses import Awards
from mongo.bsepoints.points import UserPoints
import contextlib


class AwardsBuilder:
    """Class for Awards builder."""

    def __init__(
        self: "AwardsBuilder",
        bot: BSEBot,
        guild_id: int,
        logger: Logger,
        annual: bool = False,
        debug_mode: bool = False,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_id (int): the guild ID
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            annual (bool): whether to do annual stats or monthly stats
            debug_mode (bool): whether we're running in debug mode
        """
        self.bot = bot
        self.guild_id = guild_id
        self.logger = logger
        self.annual = annual
        self.debug = debug_mode

        self.stats = StatsGatherer(logger, annual)
        self.awards = Awards()
        self.user_points = UserPoints()

    @staticmethod
    def _get_comparison_string(new_value: float, old_value: float) -> str:
        """Creates a basic comparison string we can use in stats text.

        Args:
            new_value (float | int): the incumbent stat value
            old_value (float | int): the previous stat value

        Returns:
            str: a formatted string
        """
        diff = new_value - old_value

        try:
            perc = round((diff / old_value) * 100, 2)
        except ZeroDivisionError:
            perc = 0

        if perc < 0:
            # make percentage positive
            perc *= -1

        _string = f" ({'up' if diff > 0 else 'down'} `{perc if perc != 0 else "∞"}%`)"

        if diff == 0:
            _string = " (no change)"

        return _string

    async def build_stats_and_message(  # noqa: PLR0912, C901, PLR0915
        self: "AwardsBuilder",
    ) -> tuple[list[StatDB], list[str]]:
        """Uses StatsGatherer to query for all the required stats.

        Formats an appropriate message
        Returns all the stats object and the message.

        Returns:
            tuple[list[StatDB], list[str]]: Tuple of the list Stat objects and the stats message to send
        """
        if not self.annual:
            start, end = self.stats.get_monthly_datetime_objects()
        else:
            start, end = self.stats.get_annual_datetime_objects()

        self.logger.info("Got start/end to be: %s, %s", start, end)

        args = (self.guild_id, start, end)

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
        quietest_channel = self.stats.quietest_channel(*args)
        quietest_thread = self.stats.quietest_thread(*args)
        quietest_day = self.stats.quietest_day(*args)
        emojis_created = self.stats.emojis_created(*args)

        busiest_day_format = busiest_day.value.strftime("%a %d %b")
        quietest_day_format = quietest_day.value.strftime("%a %d %b")
        most_used_emoji_mention = f"<a:{most_used_server_emoji.value}:{most_used_server_emoji.kwargs["emoji_id"]}>"

        thread_mentions = [f"<#{thread_id}>" for thread_id in threads_created.kwargs["threads"]]
        emoji_mentions = [
            f"<a:{emoji[1]}:{emoji[0]}>"
            for emoji in zip(emojis_created.kwargs["emoji_ids"], emojis_created.kwargs["emoji_names"], strict=True)
        ]

        stats = [
            number_messages,
            avg_message_chars,
            avg_message_words,
            busiest_channel,
            busiest_day,
            num_bets,
            salary_gains,
            average_wordle,
            eddies_placed,
            eddies_won,
            most_popular_channel,
            time_spent_in_vc,
            vc_most_time_spent,
            vc_most_users,
            most_used_server_emoji,
            busiest_thread,
            threads_created,
            thread_messages,
            quietest_day,
            quietest_channel,
            quietest_thread,
        ]

        if not self.annual:
            message_start = f"{start.strftime('%B')} server stats 📈:\n\n"
        else:
            message_start = f"{start.strftime('%Y')} server stats 📈:\n\n"

        if busiest_thread.value:
            b_thread_text = f"<#{busiest_thread.value}>"
            with contextlib.suppress(discord.errors.NotFound):
                busiest_thread_obj = await self.bot.fetch_channel(busiest_thread.value)
                if busiest_thread_obj.archived:
                    b_thread_text = f"`#{busiest_thread_obj.name} (archived)`"
        else:
            b_thread_text = "none"

        if quietest_thread.value:
            q_thread_text = f"<#{quietest_thread.value}>"
            with contextlib.suppress(discord.errors.NotFound):
                quietest_thread_obj = await self.bot.fetch_channel(quietest_thread.value)
                if quietest_thread_obj.archived:
                    q_thread_text = f"`#{quietest_thread_obj.name} (archived)`"
        else:
            q_thread_text = "none"

        comparisons = {}
        # stats we can compare
        for stat in [
            number_messages,
            thread_messages,
            avg_message_words,
            avg_message_chars,
            num_bets,
            salary_gains,
            average_wordle,
            eddies_placed,
            eddies_won,
            time_spent_in_vc,
        ]:
            try:
                previous = self.awards.get_previous_stat(stat)

                if not previous:
                    self.logger.debug("Couldn't find previous stat for %s", stat.short_name)
                    comparisons[stat.stat] = ""
                    continue

                comparison_string = self._get_comparison_string(stat.value, previous.value)
            except Exception:
                self.logger.exception("Got an error working out %s comparison string", stat.short_name)
                comparisons[stat.stat] = ""
                continue

            comparisons[stat.stat] = comparison_string

        # this is a mess
        stat_parts = [
            message_start,
            (
                f"- **Number of messages sent** 📬: `{number_messages.value}` (in `"
                f"{number_messages.kwargs["channels"]}` channel{'s' if thread_messages.kwargs["channels"] != 1 else ''}"
                f" from `{number_messages.kwargs["users"]}` users){comparisons.get(number_messages.stat)}\n"
            ),
            (
                f"- **Number of thread messages sent** 📟: `{thread_messages.value}` (in `"
                f"{thread_messages.kwargs["channels"]}` thread{'s' if thread_messages.kwargs["channels"] != 1 else ''} "
                f"from `{thread_messages.kwargs["users"]}` users){comparisons.get(thread_messages.stat)}\n"
            ),
            (
                f"- **Average message length** 📰: Characters (`{avg_message_chars.value}`), "
                f"Words (`{avg_message_words.value}`)\n"
            ),
            (
                f"- **Chattiest channel** 🖨️: <#{busiest_channel.value}> "
                f"(`{busiest_channel.kwargs["messages"]}` messages from `{busiest_channel.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Quietest channel** 📭: <#{quietest_channel.value}> "
                f"(`{quietest_channel.kwargs["messages"]}` messages from `{quietest_channel.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Chattiest thread** 📧: {b_thread_text} "
                f"(`{busiest_thread.kwargs["messages"]}` messages from `{busiest_thread.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Quietest thread** 📖: {q_thread_text} "
                f"(`{quietest_thread.kwargs["messages"]}` messages from `{quietest_thread.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Most popular channel** 💌: <#{most_popular_channel.value}> "
                f"(`{most_popular_channel.kwargs["users"]}` unique users)\n"
            ),
            (
                f"- **Threads created** 🖇️: {threads_created.value} ("
                f"{','.join(thread_mentions) if len(thread_mentions) < 5 else '_too many to list_'}"  # noqa: PLR2004
                ")\n"
            ),
            (
                f"- **Chattiest day** 🗓️: {busiest_day_format} "
                f"(`{busiest_day.kwargs["messages"]}` messages in `{busiest_day.kwargs["channels"]}` "
                f"channels from `{busiest_day.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Quietest day** 📆: {quietest_day_format} "
                f"(`{quietest_day.kwargs["messages"]}` messages in `{quietest_day.kwargs["channels"]}` "
                f"channels from `{quietest_day.kwargs["users"]}` users)\n"
            ),
            (
                f"- **Average wordle score** 🟩: `{average_wordle.value}` "
                f"(the bot's: `{average_wordle.kwargs["bot_average"]}`){comparisons.get(average_wordle.stat)}\n"
            ),
            (
                f"- **Total time spent in VCs** 📱: `{datetime.timedelta(seconds=time_spent_in_vc.value)!s}` "
                f"(`in {time_spent_in_vc.kwargs["channels"]}` channels from `{time_spent_in_vc.kwargs["users"]}` users)"
                f"{comparisons.get(time_spent_in_vc.stat)}\n"
            ),
            (
                f"- **Talkiest VC** 💬: <#{vc_most_time_spent.value}> "
                f"(`{vc_most_time_spent.kwargs["users"]}` users spent "
                f"`{datetime.timedelta(seconds=vc_most_time_spent.kwargs["time"])!s}` in this VC)\n"
            ),
            (
                f"- **Most popular VC** 🎉: <#{vc_most_users.value}> "
                f"(`{vc_most_users.kwargs["users"]}` unique users spent "
                f"`{datetime.timedelta(seconds=vc_most_users.kwargs["time"])!s}` in this VC)\n"
            ),
            (f"- **Bets created** 🗃️: `{num_bets.value}`{comparisons.get(num_bets.stat)}\n"),
            (f"- **Eddies gained via salary** 👩🏼‍💼: `{salary_gains.value}`{comparisons.get(salary_gains.stat)}\n"),
            (f"- **Eddies placed on bets** 🧑🏼‍💻: `{eddies_placed.value}`{comparisons.get(eddies_placed.stat)}\n"),
            (f"- **Eddies won on bets** 🧑🏼‍🏫: `{eddies_won.value}`{comparisons.get(eddies_won.stat)}\n"),
            (
                f"- **Most popular server emoji** 🗳️: {most_used_emoji_mention} "
                f"(`{most_used_server_emoji.kwargs["count"]}`)"
            ),
        ]

        if self.annual:
            stat_parts.append(
                f"\n**Emojis created** : {emojis_created.value} ({', '.join(emoji_mentions)})",
            )

        bseddies_stats = []
        message = ""
        for msg_part in stat_parts:
            if len(message + msg_part) > 1980:  # noqa: PLR2004
                bseddies_stats.append(message)
                message = ""
            message += msg_part
        bseddies_stats.append(message)

        return stats, bseddies_stats

    async def build_awards_and_message(  # noqa: PLR0915
        self: "AwardsBuilder",
    ) -> tuple[list[StatDB], list[str]]:
        """Uses StatsGatherer to gather all the awards.

        Formats an awards message
        Returns the list of awards and the message.

        Returns:
            tuple[list[StatDB], list[str]]: tuple of List of Awards and the awards messages
        """
        if not self.annual:
            start, end = self.stats.get_monthly_datetime_objects()
        else:
            start, end = self.stats.get_annual_datetime_objects()

        self.logger.info("Got start/end to be: %s, %s", start, end)

        args = (self.guild_id, start, end)

        try:
            guild = await self.bot.fetch_guild(self.guild_id)
        except discord.errors.NotFound:
            if self.debug:
                guild = await self.bot.fetch_guild(SLOMAN_SERVER_ID)
            else:
                raise

        most_messages = self.stats.most_messages_sent(*args)
        least_messages = self.stats.least_messages_sent(*args)
        longest_message = self.stats.longest_message(*args)
        best_wordle = self.stats.lowest_average_wordle_score(*args)
        worst_wordle = self.stats.highest_average_wordle_score(*args)
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
        wordle_green = self.stats.wordle_most_greens(*args)
        wordle_symmetry = self.stats.wordle_most_symmetry(*args)

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
            fattest_fingers,
            most_swears,
            single_minded,
            diverse_portfolio,
            worst_wordle,
        ]

        if not self.annual:
            message_start = f"# {start.strftime('%B')} BSEddies Awards 🏆\n"
            prize = MONTHLY_AWARDS_PRIZE
        else:
            message_start = f"# {start.strftime('%Y')} BSEddies Awards 🏆\n\n"
            prize = ANNUAL_AWARDS_AWARD

        awards_parts = [
            message_start,
            f"### Each award has a prize of **{prize}** eddies.\n\n",
            (
                # server owner award
                "- The _'server owner'_ 👨‍👧‍👦 award: " f"<@!{owner_award.user_id}>\n"
            ),
            (
                # most messages
                "- The _'won't shut up'_ 🤐 award: "
                f"<@!{most_messages.user_id}> (`{most_messages.value}` messages sent)\n"
            ),
            (
                # the longest message
                "- The _'can't find the enter key'_ ⌨️ award: "
                f"<@!{longest_message.user_id}> (`{longest_message.value}` longest message length)\n"
            ),
            (
                # most messages to a thread
                "- The _'best threads'_ 🧵 award: "
                f"<@!{threadiest_user.user_id}> (`{threadiest_user.value}` messages sent to threads)\n"
            ),
            (
                # the least messages sent
                "- The _'participation'_ 🥉 award: "
                f"<@!{least_messages.user_id}> (`{least_messages.value}` messages sent)\n"
            ),
            (
                # single minded
                "- The _'single minded'_ 🧠 award: "
                f"<@!{single_minded.user_id}> (`{single_minded.value}%` of messages "
                f"sent to <#{single_minded.kwargs["channel"]}>)\n"
            ),
            (
                # diverse portfolio
                "- The _'diverse portfolio'_ 💼 award: "
                f"<@!{diverse_portfolio.user_id}> (`{diverse_portfolio.kwargs["messages"]}` sent to "
                f"`{diverse_portfolio.value}` channels)\n"
            ),
            (
                # most replies
                "- The _'serial replier'_ 📝 award: "
                f"<@!{serial_replier.user_id}> (`{serial_replier.value}` replies)\n"
            ),
            (
                # most replied to
                "- The _'conversation started'_ 📥 award: "
                f"<@!{conversation_starter.user_id}> "
                f"(`{conversation_starter.value}` replies _received_)\n"
            ),
            (
                # twitter links
                "- The _'twitter addict'_ 🐦 award: "
                f"<@!{twitter_addict.user_id}> (`{twitter_addict.value}` tweets shared)\n"
            ),
            (
                # jerk-off-chat contribs
                "- The _'jerk off mate'_ 🍆 award: "
                f"<@!{jerk_off_king.user_id}> "
                f"(`{jerk_off_king.value}` contributions to <#{JERK_OFF_CHAT}>)\n"
            ),
            (
                # edited messages
                "- The _'fat fingers'_ 🖐🏼 award: "
                f"<@!{fattest_fingers.user_id}> (`{fattest_fingers.value}` edits to "
                f"`{fattest_fingers.kwargs["message_count"]}` messages)\n"
            ),
            (
                # most swears
                "- The _'dirtiest fingers'_ 🚽 award: " f"<@!{most_swears.user_id}> (`{most_swears.value}` swears)\n"
            ),
            (
                # best wordle score
                "- The _'I have an English degree'_ 📑 award: "
                f"<@!{best_wordle.user_id}> (`{round(best_wordle.value, 4)}` average wordle score)\n"
            ),
            (
                # worst wordle score
                "- The _'Is this bitch ESL?'_ :flag_eu: award: "
                f"<@!{worst_wordle.user_id}> (`{round(worst_wordle.value, 4)}` average wordle score)\n"
            ),
            (
                # most wordle greens score
                "- The _'Five a Day'_ 🟩 award: "
                f"<@!{wordle_green.user_id}> (`{wordle_green.value}` fully green wordle(s))\n"
            ),
            (
                # most wordle symmetry score
                "- The _'Perfectly Balanced'_ 🪞 award: "
                f"<@!{wordle_symmetry.user_id}> (`{wordle_symmetry.value}` symmetrical wordle(s))\n"
            ),
            (
                # most reacts
                "- The _'big memer'_ 😎 award: " f"<@!{big_memer.user_id}> (`{big_memer.value}` reacts received)\n"
            ),
            (
                # most reacts given
                "- The _'emoji is worth a thousand words'_ 😂 award: "
                f"<@!{react_king.user_id}> (`{react_king.value}` reacts given)\n"
            ),
            (
                # most time spent in VC
                "- The _'big talker'_ 🔊 award: "
                f"<@!{big_gamer.user_id}> "
                f"(`{datetime.timedelta(seconds=big_gamer.value)!s}` spent in "
                f"{big_gamer.kwargs["channels"]} channels)\n"
            ),
            (
                # most time streaming
                "- The _'wannabe streamer'_ 🖥️ award: "
                f"<@!{big_streamer.user_id}> (`{datetime.timedelta(seconds=big_streamer.value)!s}` "
                f"spent streaming in {big_streamer.kwargs["channels"]} channels)\n"
            ),
            (
                # most bets created
                "- The _'bookie'_ 🤑 award: " f"<@!{most_bets.user_id}> (`{most_bets.value}` bets created)\n"
            ),
            (
                # most eddies bet
                "- The _'just one more bet'_ 💵 award: "
                f"<@!{most_eddies_placed.user_id}> (`{most_eddies_placed.value}` eddies bet)\n"
            ),
            (
                # most eddies won
                "- The _'rollin' in it'_ 💰 award: "
                f"<@!{most_eddies_won.user_id}> (`{most_eddies_won.value}` eddies won)\n"
            ),
            (
                # most time king
                "- The _'king of kings'_ 👑 award: "
                f"<@!{longest_king.user_id}> "
                f"(`{datetime.timedelta(seconds=longest_king.value)!s}` spent as KING)"
            ),
        ]

        bseddies_awards = []

        message = ""
        for msg_part in awards_parts:
            if len(message + msg_part) > 1980:  # noqa: PLR2004
                bseddies_awards.append(message)
                message = ""
            message += msg_part
        bseddies_awards.append(message)

        return awards, bseddies_awards

    async def send_stats_and_awards(  # noqa: C901, PLR0912
        self: "AwardsBuilder",
        stats: list[StatDB],
        stats_message: list[str],
        awards: list[StatDB],
        awards_message: list[str],
        send_messages: bool = True,
    ) -> None:
        """Given the stats and awards - actually log those, distribute eddies and send the message.

        Args:
            stats (list[StatDB]): _description_
            stats_message (list[str]): _description_
            awards (list[StatDB]): _description_
            awards_message (list[str]): _description_
            send_messages (bool): whether to actually send messages
        """
        for stat in stats:
            if self.awards.find_entry(stat):
                self.logger.debug("Already have this stat, %s, in the database. Skipping...", stat)
                continue

            self.logger.debug("%s", {k: v for k, v in stat.__dict__.items() if v is not None})

            if self.debug:
                continue

            self.awards.document_stat(**{k: v for k, v in stat.__dict__.items() if v is not None})

        if not self.annual:
            transaction_type = TransactionTypes.MONTHLY_AWARDS_PRIZE
        else:
            transaction_type = TransactionTypes.ANNUAL_AWARDS_PRIZE

        for award in awards:
            # run this in dry run mode before committing anything

            if self.awards.find_entry(award):
                self.logger.debug("Already have this award, %s, in the database. Skipping...", award)
                continue

            self.logger.debug("%s", {k: v for k, v in award.__dict__.items() if v is not None})
            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v is not None}, dry_run=True)

        for award in awards:
            self.logger.info("%s", {k: v for k, v in award.__dict__.items() if v is not None})

            if self.debug:
                continue

            self.awards.document_award(**{k: v for k, v in award.__dict__.items() if v is not None})
            if award.user_id != BSE_BOT_ID:
                self.user_points.increment_points(
                    award.user_id,
                    award.guild_id,
                    award.eddies,
                    transaction_type,
                    award_name=award.short_name,
                )

        if self.debug:
            channel = await self.bot.fetch_channel(291508460519161856)
        else:
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)

        self.logger.info("Stats message is %s messages long", len(stats_message))
        for message in stats_message:
            self.logger.info("Stats message part is %s chars long", len(message))

            await channel.send(content=message, silent=True)
            self.logger.debug(message)

        self.logger.info("Awards message is %s messages long", len(awards_message))
        for message in awards_message:
            self.logger.info("Awards message part is %s chars long", len(message))
            if send_messages:
                await channel.send(content=message, silent=True)
            self.logger.debug(message)
