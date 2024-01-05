"""Stats classes."""

import datetime
import re
from copy import deepcopy
from logging import Logger
from typing import TYPE_CHECKING

import discord

from discordbot.bot_enums import ActivityTypes, AwardsTypes, StatTypes, TransactionTypes
from discordbot.constants import (
    ANNUAL_AWARDS_AWARD,
    BSE_BOT_ID,
    JERK_OFF_CHAT,
    MONTHLY_AWARDS_PRIZE,
    WORDLE_SCORE_REGEX,
)
from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.stats.statsdataclasses import Stat
from discordbot.utilities import PlaceHolderLogger

if TYPE_CHECKING:
    from mongo.datatypes import ReactionDB


class StatsGatherer:  # noqa: PLR0904
    """Class for stats gatherer."""

    def __init__(self, logger: Logger = PlaceHolderLogger, annual: bool = False) -> None:
        """Initialisation method.

        Args:
            logger (Logger, optional): logger to use. Defaults to PlaceHolderLogger.
            annual (bool, optional): whether to gather annual or monthly stats. Defaults to False.
        """
        self.annual = annual
        self.logger = logger
        self.cache = StatsDataCache(self.annual)

    @staticmethod
    def get_monthly_datetime_objects() -> tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous month.

        Returns:
            Tuple[datetime.datetime, datetime.datetime]:
        """
        now = datetime.datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
        try:
            start = start.replace(month=start.month - 1)
        except ValueError:
            start = start.replace(month=12, year=start.year - 1)

        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)

        return start, end

    @staticmethod
    def get_annual_datetime_objects() -> tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous year.

        Returns:
            Tuple[datetime.datetime, datetime.datetime]:
        """
        now = datetime.datetime.now()

        # always create so it's the first of the month of the current year
        end = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=1)
        # always be the first of the previous year
        start = end.replace(year=end.year - 1)

        return start, end

    def add_annual_changes(self, start: datetime.datetime, data_class: Stat) -> Stat:
        """Adds changes for annual mode.

        Args:
            start (datetime.datetime): start end time
            data_class (Stat): data class to modify

        Returns:
            Stat: the modified dataclass
        """
        if self.annual:
            data_class.month = None
            data_class.year = start.strftime("%Y")
            if data_class.type == "award":
                data_class.eddies = ANNUAL_AWARDS_AWARD
        return data_class

    # generic server stats
    def number_of_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the number of messages between two given time periods.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the number of messages stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        channel_ids = {m["channel_id"] for m in messages}
        user_ids = {m["user_id"] for m in messages}

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.NUMBER_OF_MESSAGES,
            month=start.strftime("%b %y"),
            value=len(messages),
            timestamp=datetime.datetime.now(),
            short_name="number_of_messages",
            annual=self.annual,
        )

        data_class.channels = len(channel_ids)
        data_class.users = len(user_ids)
        return self.add_annual_changes(start, data_class)

    def number_of_threaded_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the number of messages sent in threads.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the thread message stat
        """
        messages = self.cache.get_threaded_messages(guild_id, start, end)

        channel_ids = {m["channel_id"] for m in messages}
        user_ids = {m["user_id"] for m in messages}

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.NUMBER_OF_THREAD_MESSAGES,
            month=start.strftime("%b %y"),
            value=len(messages),
            timestamp=datetime.datetime.now(),
            short_name="number_of_thread_messages",
            annual=self.annual,
        )

        data_class.channels = len(channel_ids)
        data_class.users = len(user_ids)
        return self.add_annual_changes(start, data_class)

    def average_message_length(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> tuple[Stat, Stat]:
        """Returns the average message length between two given time periods.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Tuple[Stat, Stat]: returns a tuple of average message characters and average words per message stats
        """
        messages = self.cache.get_messages(guild_id, start, end)
        lengths = []
        words = []
        for message in messages:
            if content := message["content"]:
                lengths.append(len(content))
                words.append(len(content.split(" ")))
        average_message_len = round((sum(lengths) / len(lengths)), 2)
        average_word_number = round((sum(words) / len(words)), 2)

        data_class_a = Stat(
            "stat",
            guild_id,
            stat=StatTypes.AVERAGE_MESSAGE_LENGTH_CHARS,
            month=start.strftime("%b %y"),
            value=average_message_len,
            timestamp=datetime.datetime.now(),
            short_name="average_message_length_chars",
            annual=self.annual,
        )

        data_class_b = Stat(
            "stat",
            guild_id,
            stat=StatTypes.AVERAGE_MESSAGE_LENGTH_WORDS,
            month=start.strftime("%b %y"),
            value=average_word_number,
            timestamp=datetime.datetime.now(),
            short_name="average_message_length_words",
            annual=self.annual,
        )

        data_class_a = self.add_annual_changes(start, data_class_a)
        data_class_b = self.add_annual_changes(start, data_class_b)

        return data_class_a, data_class_b

    def busiest_channel(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the channel with the most messages for a given time period.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: the busiest channel stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        messages = [m for m in messages if not m.get("is_thread") and not m.get("is_vc")]

        channels = {}
        for message in messages:
            channel_id = message["channel_id"]
            user_id = message["user_id"]
            if not channel_id:
                continue
            if channel_id not in channels:
                channels[channel_id] = {"count": 0, "users": []}
            channels[channel_id]["count"] += 1
            if user_id not in channels[channel_id]["users"]:
                channels[channel_id]["users"].append(user_id)

        busiest = sorted(channels, key=lambda x: channels[x]["count"], reverse=True)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.BUSIEST_CHANNEL,
            month=start.strftime("%b %y"),
            value=busiest,
            timestamp=datetime.datetime.now(),
            short_name="busiest_channel",
            annual=self.annual,
        )

        data_class.messages = channels[busiest]["count"]
        data_class.users = len(channels[busiest]["users"])
        data_class.channels = {str(k): v for k, v in channels.items()}
        return self.add_annual_changes(start, data_class)

    def busiest_thread(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the thread with most messages for the given time period.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: the stat class
        """
        threaded = self.cache.get_threaded_messages(guild_id, start, end)

        threads = {}
        for thread_message in threaded:
            thread_id = thread_message["channel_id"]
            user_id = thread_message["user_id"]

            if thread_id not in threads:
                threads[thread_id] = {"count": 0, "users": []}
            threads[thread_id]["count"] += 1

            if user_id not in threads[thread_id]["users"]:
                threads[thread_id]["users"].append(user_id)

        try:
            busiest = sorted(threads, key=lambda x: threads[x]["count"], reverse=True)[0]
        except IndexError:
            busiest = 0
            threads[0] = {"count": 0, "users": []}

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.BUSIEST_THREAD,
            month=start.strftime("%b %y"),
            value=busiest,
            timestamp=datetime.datetime.now(),
            short_name="busiest_thread",
            annual=self.annual,
        )
        data_class.messages = threads[busiest]["count"]
        data_class.users = len(threads[busiest]["users"])
        data_class.threads = {str(k): v for k, v in threads.items()}
        return self.add_annual_changes(start, data_class)

    def busiest_day(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the day with the most messages sent for the given time period.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: the busiest day stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        days = {}
        for message in messages:
            channel_id = message["channel_id"]
            user_id = message["user_id"]
            day = message["timestamp"].date()
            if day not in days:
                days[day] = {"count": 0, "channels": [], "users": []}
            days[day]["count"] += 1

            if channel_id not in days[day]["channels"]:
                days[day]["channels"].append(channel_id)
            if user_id not in days[day]["users"]:
                days[day]["users"].append(user_id)

        busiest = sorted(days, key=lambda x: days[x]["count"], reverse=True)[0]  # type: datetime.date

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.BUSIEST_DAY,
            month=start.strftime("%b %y"),
            value=busiest,
            timestamp=datetime.datetime.now(),
            short_name="busiest_day",
            annual=self.annual,
        )

        data_class.messages = days[busiest]["count"]
        data_class.channels = len(days[busiest]["channels"])
        data_class.users = len(days[busiest]["users"])
        return self.add_annual_changes(start, data_class)

    def quietest_channel(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        channel_ids: list[int] | None = None,
    ) -> Stat:
        """Returns the channel with the least messages for a given time period.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period
            channel_ids (list[int]): list of channel IDs

        Returns:
            Stat: the quietest channel stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        messages = [m for m in messages if not m.get("is_thread") and not m.get("is_vc")]

        channels = {}
        for message in messages:
            channel_id = message["channel_id"]
            user_id = message["user_id"]
            if not channel_id or (channel_ids and channel_id not in channel_ids):
                continue
            if channel_id not in channels:
                channels[channel_id] = {"count": 0, "users": []}
            channels[channel_id]["count"] += 1
            if user_id not in channels[channel_id]["users"]:
                channels[channel_id]["users"].append(user_id)

        quietest = sorted(channels, key=lambda x: channels[x]["count"], reverse=False)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.QUIETEST_CHANNEL,
            month=start.strftime("%b %y"),
            value=quietest,
            timestamp=datetime.datetime.now(),
            short_name="quietest_channel",
            annual=self.annual,
        )

        data_class.messages = channels[quietest]["count"]
        data_class.users = len(channels[quietest]["users"])
        data_class.channels = {str(k): v for k, v in channels.items()}
        return self.add_annual_changes(start, data_class)

    def quietest_thread(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the quietest thread.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: the quietest thread stat
        """
        threaded = self.cache.get_threaded_messages(guild_id, start, end)

        threads = {}
        for thread_message in threaded:
            thread_id = thread_message["channel_id"]
            user_id = thread_message["user_id"]

            if thread_id not in threads:
                threads[thread_id] = {"count": 0, "users": []}
            threads[thread_id]["count"] += 1

            if user_id not in threads[thread_id]["users"]:
                threads[thread_id]["users"].append(user_id)

        try:
            quietest = sorted(threads, key=lambda x: threads[x]["count"], reverse=False)[0]
        except IndexError:
            quietest = 0
            threads[0] = {"count": 0, "users": []}

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.QUIETEST_THREAD,
            month=start.strftime("%b %y"),
            value=quietest,
            timestamp=datetime.datetime.now(),
            short_name="quietest_thread",
            annual=self.annual,
        )
        data_class.messages = threads[quietest]["count"]
        data_class.users = len(threads[quietest]["users"])
        data_class.threads = {str(k): v for k, v in threads.items()}
        return self.add_annual_changes(start, data_class)

    def quietest_day(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the day with the least messages sent for the given time period.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: the quietest day stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        days = {}
        for message in messages:
            channel_id = message["channel_id"]
            user_id = message["user_id"]
            day = message["timestamp"].date()
            if day not in days:
                days[day] = {"count": 0, "channels": [], "users": []}
            days[day]["count"] += 1

            if channel_id not in days[day]["channels"]:
                days[day]["channels"].append(channel_id)
            if user_id not in days[day]["users"]:
                days[day]["users"].append(user_id)

        quietest = sorted(days, key=lambda x: days[x]["count"], reverse=False)[0]  # type: datetime.date

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.QUIETEST_DAY,
            month=start.strftime("%b %y"),
            value=quietest,
            timestamp=datetime.datetime.now(),
            short_name="quietest_day",
            annual=self.annual,
        )

        data_class.messages = days[quietest]["count"]
        data_class.channels = len(days[quietest]["channels"])
        data_class.users = len(days[quietest]["users"])
        return self.add_annual_changes(start, data_class)

    def number_of_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the number of bets between two given time periods.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the number of bets stat
        """
        bets = self.cache.get_bets(guild_id, start, end)

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.NUMBER_OF_BETS,
            month=start.strftime("%b %y"),
            value=len(bets),
            timestamp=datetime.datetime.now(),
            short_name="number_of_bets",
            annual=self.annual,
        )

        return self.add_annual_changes(start, data_class)

    def salary_gains(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the total amount of eddies gained through salaries this month.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the salary stat
        """
        transactions = self.cache.get_transactions(guild_id, start, end)
        salary_total = 0
        for trans in transactions:
            if trans.type != TransactionTypes.DAILY_SALARY:
                continue
            salary_total += trans.amount

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.SALARY_GAINS,
            month=start.strftime("%b %y"),
            value=salary_total,
            timestamp=datetime.datetime.now(),
            short_name="salary_total",
            annual=self.annual,
        )

        return self.add_annual_changes(start, data_class)

    def average_wordle_victory(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the server's average wordle score.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: average wordle stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]

        wordle_count = []
        for wordle in wordle_messages:
            if wordle["user_id"] == BSE_BOT_ID:
                continue

            result = re.search(WORDLE_SCORE_REGEX, wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "10"
            guesses = int(guesses)
            wordle_count.append(guesses)

        bot_wordles = self.cache.user_interactions.paginated_query(
            {"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}, "message_type": "wordle", "is_bot": True},
        )
        bot_wordle_count = []
        for wordle in bot_wordles:
            if wordle["user_id"] != BSE_BOT_ID:
                continue

            result = re.search(WORDLE_SCORE_REGEX, wordle["content"]).group()
            guesses = result.split("/")[0]
            if guesses == "X":
                guesses = "10"
            guesses = int(guesses)
            bot_wordle_count.append(guesses)

        average_wordle = round((sum(wordle_count) / len(wordle_count)), 4)
        average_bot_wordle = round((sum(bot_wordle_count) / len(bot_wordle_count)), 4)

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.AVERAGE_WORDLE_VICTORY,
            month=start.strftime("%b %y"),
            value=average_wordle,
            timestamp=datetime.datetime.now(),
            short_name="average_wordle_victory",
            annual=self.annual,
        )

        data_class.bot_average = average_bot_wordle
        return self.add_annual_changes(start, data_class)

    def bet_eddies_stats(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> tuple[Stat, Stat]:
        """Calculates the total eddies placed on bets, and the total eddies won on bets.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[Stat, Stat]: returns a tuple of eddies placed and eddies won
        """
        transactions = self.cache.get_transactions(guild_id, start, end)

        eddies_placed = 0
        eddies_won = 0
        for trans in transactions:
            trans_type = trans.type
            if trans_type == TransactionTypes.BET_PLACE:
                eddies_placed -= trans.amount  # amount is negative in these cases
            elif trans_type == TransactionTypes.BET_WIN:
                eddies_won += trans.amount

        data_class_a = Stat(
            "stat",
            guild_id,
            stat=StatTypes.EDDIES_PLACED,
            month=start.strftime("%b %y"),
            value=eddies_placed,
            timestamp=datetime.datetime.now(),
            short_name="number_of_eddies_placed",
            annual=self.annual,
        )

        data_class_b = Stat(
            "stat",
            guild_id,
            stat=StatTypes.EDDIES_WIN,
            month=start.strftime("%b %y"),
            value=eddies_won,
            timestamp=datetime.datetime.now(),
            short_name="number_of_eddies_won",
            annual=self.annual,
        )

        data_class_a = self.add_annual_changes(start, data_class_a)
        data_class_b = self.add_annual_changes(start, data_class_b)

        return data_class_a, data_class_b

    def most_unique_channel_contributers(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the channel with the most unique contributors.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: channel contrib stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        channels = {}
        for message in messages:
            channel_id = message["channel_id"]
            user_id = message["user_id"]
            if channel_id not in channels:
                channels[channel_id] = []
            if user_id not in channels[channel_id]:
                channels[channel_id].append(user_id)

        most_popular_channel = sorted(channels, key=lambda x: len(channels[x]), reverse=True)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.MOST_POPULAR_CHANNEL,
            month=start.strftime("%b %y"),
            value=most_popular_channel,
            timestamp=datetime.datetime.now(),
            short_name="most_popular_channel",
            annual=self.annual,
        )

        data_class.users = len(channels[most_popular_channel])

        return self.add_annual_changes(start, data_class)

    def total_time_spent_in_vc(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the total amount of time spent by everyone in all VCs.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: time spent in VC stat
        """
        vc_interactions = self.cache.get_vc_interactions(guild_id, start, end)
        vc_time = 0
        channels = []
        users = []

        for interaction in vc_interactions:
            time_spent = interaction["time_in_vc"]
            user_id = interaction["user_id"]
            channel_id = interaction["channel_id"]
            vc_time += time_spent
            if channel_id not in channels:
                channels.append(channel_id)
            if user_id not in users:
                users.append(user_id)

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.TIME_SPENT_IN_VC,
            month=start.strftime("%b %y"),
            value=int(vc_time),
            timestamp=datetime.datetime.now(),
            short_name="total_time_spent_in_vc",
            annual=self.annual,
        )

        data_class.users = len(users)
        data_class.channels = len(channels)

        return self.add_annual_changes(start, data_class)

    def vc_with_most_time_spent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which VC had the most time spent in it.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the VC stat
        """
        vc_interactions = self.cache.get_vc_interactions(guild_id, start, end)

        channels = {}

        for interaction in vc_interactions:
            time_spent = interaction["time_in_vc"]
            user_id = interaction["user_id"]
            channel_id = interaction["channel_id"]
            if channel_id not in channels:
                channels[channel_id] = {"count": 0, "users": []}
            channels[channel_id]["count"] += time_spent
            if user_id not in channels[channel_id]["users"]:
                channels[channel_id]["users"].append(user_id)

        vc_most_time = sorted(channels, key=lambda x: channels[x]["count"], reverse=True)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.VC_MOST_TIME,
            month=start.strftime("%b %y"),
            value=vc_most_time,
            timestamp=datetime.datetime.now(),
            short_name="vc_most_time",
            annual=self.annual,
        )

        data_class.users = len(channels[vc_most_time]["users"])
        data_class.channels = {str(k): v for k, v in channels.items()}
        data_class.time = int(channels[vc_most_time]["count"])

        return self.add_annual_changes(start, data_class)

    def vc_with_most_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which VC had the most unique users in it.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the VC stat
        """
        vc_interactions = self.cache.get_vc_interactions(guild_id, start, end)

        channels = {}

        for interaction in vc_interactions:
            time_spent = interaction["time_in_vc"]
            user_id = interaction["user_id"]
            channel_id = interaction["channel_id"]
            if channel_id not in channels:
                channels[channel_id] = {"count": 0, "users": []}
            channels[channel_id]["count"] += time_spent
            if user_id not in channels[channel_id]["users"]:
                channels[channel_id]["users"].append(user_id)

        vc_most_users = sorted(channels, key=lambda x: len(channels[x]["users"]), reverse=True)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.VC_MOST_TIME,
            month=start.strftime("%b %y"),
            value=vc_most_users,
            timestamp=datetime.datetime.now(),
            short_name="vc_most_time",
            annual=self.annual,
        )
        data_class.time = int(channels[vc_most_users]["count"])
        data_class.channels = {str(k): v for k, v in channels.items()}
        data_class.users = len(channels[vc_most_users]["users"])

        return self.add_annual_changes(start, data_class)

    def most_popular_server_emoji(  # noqa: C901, PLR0912
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        uid: int | None = None,
    ) -> Stat:
        """Calculates the most popular server emoji for the given time frame.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period
            uid (int): optional - filter reacts to a particular user

        Returns:
            Stat: the ServerEmoji data class
        """
        reaction_messages = self.cache.get_reactions(guild_id, start, end)
        messages = self.cache.get_messages(guild_id, start, end)

        reactions: list[ReactionDB] = []
        for react in reaction_messages:
            if uid:
                # filter the reactions to our uid
                _reactions = [r for r in react.reactions if r.user_id == uid]
                if not _reactions:
                    continue
            else:
                _reactions = react.reactions
            reactions.extend(_reactions)

        all_emojis = self.cache.get_emojis(guild_id, start, end)
        all_emoji_names = [emoji.name for emoji in all_emojis]

        emoji_count = {}
        for reaction in reactions:
            content = reaction.content
            if content not in all_emoji_names:
                continue
            if content not in emoji_count:
                emoji_count[content] = 0
            emoji_count[content] += 1

        for message in messages:
            for emoji_name in all_emoji_names:
                if emojis := re.findall(f":{emoji_name}:", message.content):
                    if emoji_name not in emoji_count:
                        emoji_count[emoji_name] = 0
                    emoji_count[emoji_name] += len(emojis)

        try:
            most_used_emoji = sorted(emoji_count, key=lambda x: emoji_count[x], reverse=True)[0]

            emoji_id = next(emoji.eid for emoji in all_emojis if emoji.name == most_used_emoji)
        except IndexError:
            most_used_emoji = 0
            emoji_id = None
            emoji_count[0] = None

        data_class = Stat(
            type="stat",
            guild_id=guild_id,
            stat=StatTypes.MOST_POPULAR_SERVER_EMOJI,
            month=start.strftime("%b %y"),
            value=most_used_emoji,
            timestamp=datetime.datetime.now(),
            short_name="most_used_server_emoji",
            annual=self.annual,
        )

        data_class.emojis = emoji_count
        data_class.count = emoji_count[most_used_emoji]
        data_class.emoji_id = emoji_id

        return self.add_annual_changes(start, data_class)

    def threads_created(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates number of threads created in the given time period.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the Stat data class
        """
        created_threads = []
        all_threads = self.cache.threads.get_all_threads(guild_id)
        for thread in all_threads:
            if thread.created < start or end < thread.created:
                # thread creation falls outside our time perioud
                continue
            created_threads.append(thread)

        data_class = Stat(
            type="stat",
            guild_id=guild_id,
            stat=StatTypes.THREADS_CREATED,
            month=start.strftime("%b %y"),
            value=len(created_threads),
            timestamp=datetime.datetime.now(),
            short_name="threads_created",
            annual=self.annual,
        )

        data_class.threads = [thread.thread_id for thread in created_threads]
        return self.add_annual_changes(start, data_class)

    def emojis_created(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Gets all emojis created during the given time frame.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the emojis created stat
        """
        all_server_emojis = self.cache.server_emojis.get_all_emojis(guild_id)
        created = [e for e in all_server_emojis if start < e["created"] < end]

        data_class = Stat(
            type="stat",
            guild_id=guild_id,
            stat=StatTypes.EMOJIS_CREATED,
            month=start.strftime("%b %y"),
            value=len(created),
            timestamp=datetime.datetime.now(),
            short_name="emojis_created",
            annual=self.annual,
        )

        data_class.emoji_ids = [e["eid"] for e in created]
        return self.add_annual_changes(start, data_class)

    # stats that can be won
    # messages
    def server_owner(self, guild: discord.Guild, start: datetime.datetime) -> Stat:
        """Generates the server owner award.

        Args:
            guild (discord.Guild): the guild object

        Returns:
            Stat: the server owner award
        """
        owner = guild.owner_id

        data_class = Stat(
            type="award",
            guild_id=guild.id,
            user_id=owner,
            award=AwardsTypes.GUILD_OWNER_AWARD,
            month=start.strftime("%b %y"),
            value=guild.created_at,
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="guild_owner_award",
            annual=self.annual,
        )

        return self.add_annual_changes(start, data_class)

    def most_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the person who has sent the most messages in the server.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the most messages stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        message_users = {}
        for message in messages:
            uid = message["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in message_users:
                message_users[uid] = {"count": 0, "channels": [], "threads": []}
            message_users[uid]["count"] += 1
            if message.get("is_thread"):
                if message["channel_id"] not in message_users[uid]["threads"]:
                    message_users[uid]["threads"].append(message["channel_id"])
            elif message["channel_id"] not in message_users[uid]["channels"]:
                message_users[uid]["channels"].append(message["channel_id"])

        try:
            chattiest = sorted(message_users, key=lambda x: message_users[x]["count"], reverse=True)[0]
        except IndexError:
            chattiest = BSE_BOT_ID
            message_users[BSE_BOT_ID] = {"count": 0}

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=chattiest,
            award=AwardsTypes.MOST_MESSAGES,
            month=start.strftime("%b %y"),
            value=message_users[chattiest]["count"],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_messages_sent",
            annual=self.annual,
        )

        data_class.message_users = {str(k): v for k, v in message_users.items()}
        return self.add_annual_changes(start, data_class)

    def least_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the person who has sent the least messages in the server.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: least messages stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        message_users = {}
        for message in messages:
            uid = message["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in message_users:
                message_users[uid] = 0
            message_users[uid] += 1

        try:
            least_chattiest = sorted(message_users, key=lambda x: message_users[x])[0]
        except IndexError:
            least_chattiest = BSE_BOT_ID
            message_users[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=least_chattiest,
            award=AwardsTypes.LEAST_MESSAGES,
            month=start.strftime("%b %y"),
            value=message_users[least_chattiest],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="least_messages_sent",
            annual=self.annual,
        )

        data_class.message_users = {str(k): v for k, v in message_users.items()}
        return self.add_annual_changes(start, data_class)

    def most_thread_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the person who has sent the most threaded messages in the server.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the most thread messages stat
        """
        messages = self.cache.get_threaded_messages(guild_id, start, end)

        message_users = {}
        for message in messages:
            uid = message["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in message_users:
                message_users[uid] = 0
            message_users[uid] += 1

        try:
            chattiest = sorted(message_users, key=lambda x: message_users[x], reverse=True)[0]
        except IndexError:
            chattiest = BSE_BOT_ID
            message_users[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=chattiest,
            award=AwardsTypes.MOST_MESSAGES,
            month=start.strftime("%b %y"),
            value=message_users[chattiest],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_thread_messages_sent",
            annual=self.annual,
        )

        data_class.message_users = {str(k): v for k, v in message_users.items()}
        return self.add_annual_changes(start, data_class)

    def longest_message(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the longest message from two given time periods.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the longest message stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        longest_message = None
        for message in messages:
            if message["user_id"] == BSE_BOT_ID:
                continue
            if content := message["content"]:
                if not longest_message:
                    longest_message = message
                    continue
                if len(content) > len(longest_message["content"]):
                    longest_message = message

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=longest_message["user_id"],
            award=AwardsTypes.LONGEST_MESSAGE,
            month=start.strftime("%b %y"),
            value=len(longest_message["content"]),
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="longest_message",
            annual=self.annual,
        )

        return self.add_annual_changes(start, data_class)

    def lowest_average_wordle_score(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which user has the best average wordle score.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the wordle stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]

        # number of days in the time period
        days = (end - start).days
        threshold = round(days / 2)

        wordle_count = {}
        for wordle in wordle_messages:
            uid = wordle["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in wordle_count:
                wordle_count[uid] = []

            result = re.search(r"[\dX]/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "7"
            guesses = int(guesses)

            wordle_count[uid].append(guesses)

        if len(wordle_count) > 1:
            wordle_count_old = deepcopy(wordle_count)
            for uid in wordle_count_old:
                if len(wordle_count_old[uid]) < threshold:
                    # user hasn't done enough wordles in this time period to be
                    # counted
                    self.logger.debug(
                        "Removing %s from wordle pool as they've only done %s wordles.", uid, len(wordle_count[uid])
                    )
                    wordle_count.pop(uid)
        else:
            self.logger.debug("Length of wordle count (%s) is less than one - skipping threshold", len(wordle_count))
        wordle_avgs = {}
        for uid in wordle_count:
            all_guesses = wordle_count[uid]
            avg = sum(all_guesses) / len(all_guesses)
            wordle_avgs[uid] = avg

        try:
            best_avg = sorted(wordle_avgs, key=lambda x: wordle_avgs[x])[0]
        except IndexError:
            # no data - possible if they've never done a wordle
            best_avg = BSE_BOT_ID
            wordle_avgs[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=best_avg,
            award=AwardsTypes.BEST_AVG_WORDLE,
            month=start.strftime("%b %y"),
            value=wordle_avgs[best_avg],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="lowest_avg_wordle",
            annual=self.annual,
        )

        data_class.wordle_avgs = {str(k): v for k, v in wordle_avgs.items()}
        return self.add_annual_changes(start, data_class)

    def highest_average_wordle_score(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which user has the worst average wordle score.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the wordle stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]

        # number of days in the time period
        days = (end - start).days
        threshold = round(days / 2)

        wordle_count = {}
        for wordle in wordle_messages:
            uid = wordle["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in wordle_count:
                wordle_count[uid] = []

            result = re.search(r"[\dX]/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "7"
            guesses = int(guesses)

            wordle_count[uid].append(guesses)

        if len(wordle_count) > 1:
            wordle_count_old = deepcopy(wordle_count)
            for uid in wordle_count_old:
                if len(wordle_count_old[uid]) < threshold:
                    # user hasn't done enough wordles in this time period to be
                    # counted
                    self.logger.debug(
                        "Removing %s from wordle pool as they've only done %s wordles.", uid, len(wordle_count[uid])
                    )
                    wordle_count.pop(uid)
        else:
            self.logger.debug("Length of wordle count (%s) is less than one - skipping threshold", len(wordle_count))

        wordle_avgs = {}
        for uid in wordle_count:
            all_guesses = wordle_count[uid]
            avg = sum(all_guesses) / len(all_guesses)
            wordle_avgs[uid] = avg

        try:
            worst_avg = sorted(wordle_avgs, key=lambda x: wordle_avgs[x], reverse=True)[0]
        except IndexError:
            # no data - possible if they've never done a wordle
            worst_avg = BSE_BOT_ID
            wordle_avgs[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=worst_avg,
            award=AwardsTypes.WORST_AVG_WORDLE,
            month=start.strftime("%b %y"),
            value=wordle_avgs[worst_avg],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="highest_avg_wordle",
            annual=self.annual,
        )

        data_class.wordle_avgs = {str(k): v for k, v in wordle_avgs.items()}
        return self.add_annual_changes(start, data_class)

    def twitter_addict(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's posted the most twitter links.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: twitter stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        tweet_users = {}
        for message in messages:
            if (
                "twitter" in message["content"]
                or "https://x.com/" in message["content"]
                and "link" in message["message_type"]
            ):
                user_id = message["user_id"]
                if user_id not in tweet_users:
                    tweet_users[user_id] = 0
                tweet_users[user_id] += 1

        try:
            twitter_addict = sorted(tweet_users, key=lambda x: tweet_users[x], reverse=True)[0]
        except IndexError:
            # no data for anyone yet
            twitter_addict = 0
            tweet_users[0] = None

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=twitter_addict,
            award=AwardsTypes.TWITTER_ADDICT,
            month=start.strftime("%b %y"),
            value=tweet_users[twitter_addict],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="twitter_addict",
            annual=self.annual,
        )

        data_class.twitter_addict = {str(k): v for k, v in tweet_users.items()}
        return self.add_annual_changes(start, data_class)

    def jerk_off_contributor(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's posted this most contributions in #jerk-off-chat.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: jerk off stat
        """
        messages = self.cache.get_messages(guild_id, start, end)
        jerk_off_messages = [m for m in messages if m["channel_id"] == JERK_OFF_CHAT]

        jerk_off_users = {}
        for message in jerk_off_messages:
            if any(a for a in ["link", "attachment"] if a in message["message_type"]):
                user_id = message["user_id"]
                if user_id not in jerk_off_users:
                    jerk_off_users[user_id] = 0
                jerk_off_users[user_id] += 1

        try:
            masturbator = sorted(jerk_off_users, key=lambda x: jerk_off_users[x], reverse=True)[0]
        except IndexError:
            # no data
            masturbator = 0
            jerk_off_users[0] = None

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=masturbator,
            award=AwardsTypes.MASTURBATOR,
            month=start.strftime("%b %y"),
            value=jerk_off_users[masturbator],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="masturbator",
            annual=self.annual,
        )

        data_class.masturbators = {str(k): v for k, v in jerk_off_users.items()}
        return self.add_annual_changes(start, data_class)

    def big_memer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which user had the most reactions for this time period.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: big memeer stat
        """
        reaction_messages = self.cache.get_reactions(guild_id, start, end)

        reaction_users = {}
        for message in reaction_messages:
            user_id = message["user_id"]
            if user_id not in reaction_users:
                reaction_users[user_id] = 0
            reactions = [r for r in message["reactions"] if r["user_id"] != user_id]
            reaction_users[user_id] += len(reactions)

        big_memer = sorted(reaction_users, key=lambda x: reaction_users[x], reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=big_memer,
            award=AwardsTypes.BIG_MEMER,
            month=start.strftime("%b %y"),
            value=reaction_users[big_memer],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="big_memer",
            annual=self.annual,
        )

        data_class.reactees = {str(k): v for k, v in reaction_users.items()}
        return self.add_annual_changes(start, data_class)

    def react_king(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's given the most reactions.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period.

        Returns:
            Stat: the react king award
        """
        reaction_messages = self.cache.get_reactions(guild_id, start, end)
        reactions = []
        for react in reaction_messages:
            reactions.extend(react["reactions"])

        reaction_users = {}
        for reaction in reactions:
            user_id = reaction["user_id"]
            if user_id not in reaction_users:
                reaction_users[user_id] = 0
            reaction_users[user_id] += 1

        react_king = sorted(reaction_users, key=lambda x: reaction_users[x], reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=react_king,
            award=AwardsTypes.REACT_KING,
            month=start.strftime("%b %y"),
            value=reaction_users[react_king],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="react_king",
            annual=self.annual,
        )

        data_class.reaction_users = {str(k): v for k, v in reaction_users.items()}
        return self.add_annual_changes(start, data_class)

    def most_replies(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> tuple[Stat, Stat]:
        """Calculates who's been replied to most and who's given the most replies.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period.

        Returns:
            Tuple[Stat, Stat]: the two reply Stat objects
        """
        messages_with_replies = self.cache.get_replies(guild_id, start, end)
        replies = {}  # replies someone has done
        replied_to = {}  # replies _received_
        for message in messages_with_replies:
            _replies = message["replies"]
            m_user_id = message["user_id"]
            if m_user_id not in replied_to:
                replied_to[m_user_id] = 0
            for reply in _replies:
                if not (start < reply["timestamp"] < end):
                    continue
                replied_to[m_user_id] += 1
                user_id = reply["user_id"]
                if user_id not in replies:
                    replies[user_id] = 0
                replies[user_id] += 1

        serial_replier = sorted(replies, key=lambda x: replies[x], reverse=True)[0]
        conversation_starter = sorted(replied_to, key=lambda x: replied_to[x], reverse=True)[0]

        replier_data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=serial_replier,
            award=AwardsTypes.SERIAL_REPLIER,
            month=start.strftime("%b %y"),
            value=replies[serial_replier],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="serial_replier",
            annual=self.annual,
        )

        replier_data_class.repliers = {str(k): v for k, v in replies.items()}
        replier_data_class = self.add_annual_changes(start, replier_data_class)

        conversation_data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=conversation_starter,
            award=AwardsTypes.CONVERSATION_STARTER,
            month=start.strftime("%b %y"),
            value=replied_to[conversation_starter],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="conversation_starter",
            annual=self.annual,
        )

        conversation_data_class.repliees = {str(k): v for k, v in replied_to.items()}
        conversation_data_class = self.add_annual_changes(start, conversation_data_class)

        return replier_data_class, conversation_data_class

    def most_edited_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the user who's edited the most messages this period.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the stat object
        """
        edited_messages = self.cache.get_edited_messages(guild_id, start, end)
        message_users = {}
        for message in edited_messages:
            uid = message["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in message_users:
                message_users[uid] = {"count": 0, "messages": 0}
            message_users[uid]["count"] += message["edit_count"]
            message_users[uid]["messages"] += 1

        try:
            fattest_fingers = sorted(message_users, key=lambda x: message_users[x]["count"], reverse=True)[0]
        except IndexError:
            fattest_fingers = 0
            message_users = {0: {"count": 0, "messages": 0}}

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=fattest_fingers,
            award=AwardsTypes.FAT_FINGERS,
            month=start.strftime("%b %y"),
            value=message_users[fattest_fingers]["count"],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_messages_edited",
            annual=self.annual,
        )

        data_class.message_users = {str(k): v for k, v in message_users.items()}
        data_class.message_count = message_users[fattest_fingers]["messages"]

        return self.add_annual_changes(start, data_class)

    def most_swears(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who swore the most during the given time period.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the most swears stat
        """
        swears = ["fuck", "shit", "cunt", "piss", "cock", "bollock", "dick", "twat"]
        all_messages = self.cache.get_messages(guild_id, start, end)

        swear_dict = {}
        for message in all_messages:
            uid = message["user_id"]
            content = message.get("content")
            if content is None or content is False:
                continue

            if uid not in swear_dict:
                swear_dict[uid] = 0
            swear_count = 0
            for swear in swears:
                swear_count += content.count(swear)
            swear_dict[uid] += swear_count

        try:
            most_swears = sorted(swear_dict, key=lambda x: swear_dict[x], reverse=True)[0]
        except IndexError:
            most_swears = 0
            swear_dict[0] = None

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=most_swears,
            award=AwardsTypes.POTTY_MOUTH,
            month=start.strftime("%b %y"),
            value=swear_dict[most_swears],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_swears",
            annual=self.annual,
        )
        data_class.swears = {str(k): v for k, v in swear_dict.items()}
        return self.add_annual_changes(start, data_class)

    def most_messages_to_a_single_channel(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> Stat:
        """Calculates the user who sent most of their messages to one channel.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        users = {}
        for message in messages:
            user_id = message["user_id"]
            channel_id = message["channel_id"]

            if user_id not in users:
                users[user_id] = {"total": 0}
            if str(channel_id) not in users[user_id]:
                users[user_id][str(channel_id)] = 0

            users[user_id][str(channel_id)] += 1
            users[user_id]["total"] += 1

        # calc highest percentage
        for user in users:
            u_dict = users[user]
            total = u_dict.pop("total")
            top_channel_id = sorted(u_dict, key=lambda x: u_dict[x], reverse=True)[0]
            percentage = (u_dict[top_channel_id] / total) * 100
            u_dict["total"] = total
            u_dict["percentage"] = percentage
            u_dict["channel"] = int(top_channel_id)

        # sort the percentages
        top = sorted(users, key=lambda x: users[x]["percentage"], reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=top,
            award=AwardsTypes.SINGLE_MINDED,
            month=start.strftime("%b %y"),
            value=users[top]["percentage"],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="single_minded",
            annual=self.annual,
        )
        data_class.users = {str(k): v for k, v in users.items()}
        data_class.channel = users[top]["channel"]
        return self.add_annual_changes(start, data_class)

    def most_messages_to_most_channels(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the user who sent most of their messages to the most diverse channels.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the stat
        """
        messages = self.cache.get_messages(guild_id, start, end)

        users = {}
        for message in messages:
            user_id = message["user_id"]
            channel_id = message["channel_id"]

            if user_id not in users:
                users[user_id] = {"channels": {}, "messages": 0}
            if str(channel_id) not in users[user_id]["channels"]:
                users[user_id]["channels"][str(channel_id)] = 0
            users[user_id]["messages"] += 1
            users[user_id]["channels"][str(channel_id)] += 1

        # sort the channels
        top = sorted(users, key=lambda x: len(users[x]["channels"]), reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=top,
            award=AwardsTypes.DIVERSE_PORTFOLIO,
            month=start.strftime("%b %y"),
            value=len(users[top]["channels"]),
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="diverse_portfolio",
            annual=self.annual,
        )
        data_class.users = {str(k): v for k, v in users.items()}
        data_class.messages = users[top]["messages"]
        return self.add_annual_changes(start, data_class)

    # bets
    def most_bets_created(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Get the user who made the most bets.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: most bets stat
        """
        bets = self.cache.get_bets(guild_id, start, end)
        bet_users = {}
        for bet in bets:
            u = bet.user
            if u not in bet_users:
                bet_users[u] = 0
            bet_users[u] += 1

        try:
            busiest = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        except IndexError:
            # no bets were created this month
            busiest = BSE_BOT_ID
            bet_users[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=busiest,
            award=AwardsTypes.MOST_BETS,
            month=start.strftime("%b %y"),
            value=bet_users[busiest],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_bets_created",
            annual=self.annual,
        )

        data_class.bookies = {str(k): v for k, v in bet_users.items()}
        return self.add_annual_changes(start, data_class)

    def most_eddies_bet(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who placed the most eddies on bets.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: most eddies bet stat
        """
        transactions = self.cache.get_transactions(guild_id, start, end)

        bet_users = {}
        for trans in transactions:
            if trans.type != TransactionTypes.BET_PLACE:
                continue
            if trans.uid not in bet_users:
                bet_users[trans.uid] = 0
            bet_users[trans.uid] -= trans.amount

        try:
            most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        except IndexError:
            most_placed = BSE_BOT_ID
            bet_users[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=most_placed,
            award=AwardsTypes.MOST_EDDIES_BET,
            month=start.strftime("%b %y"),
            value=bet_users[most_placed],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_eddies_placed",
            annual=self.annual,
        )

        data_class.betters = {str(k): v for k, v in bet_users.items()}
        return self.add_annual_changes(start, data_class)

    def most_eddies_won(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who won the most eddies on bets.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: most eddies won stat
        """
        transactions = self.cache.get_transactions(guild_id, start, end)

        bet_users = {}
        for trans in transactions:
            if trans.type != TransactionTypes.BET_WIN:
                continue
            if trans.uid not in bet_users:
                bet_users[trans.uid] = 0
            bet_users[trans.uid] += trans.amount

        try:
            most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        except IndexError:
            most_placed = BSE_BOT_ID
            bet_users[BSE_BOT_ID] = 0

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=most_placed,
            award=AwardsTypes.MOST_EDDIES_WON,
            month=start.strftime("%b %y"),
            value=bet_users[most_placed],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_eddies_won",
            annual=self.annual,
        )

        data_class.bet_winners = {str(k): v for k, v in bet_users.items()}
        return self.add_annual_changes(start, data_class)

    def most_time_king(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's been King longest this month.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: longest King stat
        """
        activity_history = self.cache.get_activities(guild_id, start, end)
        king_events = sorted(
            [act for act in activity_history if act.type in {ActivityTypes.KING_GAIN, ActivityTypes.KING_LOSS}],
            key=lambda x: x["timestamp"],
        )

        kings = {}
        previous_time = start

        for event in king_events:
            if event["type"] == ActivityTypes.KING_LOSS:
                uid = event["uid"]

                timestamp = event["timestamp"]  # type: datetime.datetime
                time_king = (timestamp - previous_time).total_seconds()

                if uid not in kings:
                    kings[uid] = 0
                kings[uid] += time_king
                previous_time = None

            elif event["type"] == ActivityTypes.KING_GAIN:
                previous_time = event["timestamp"]

        if king_events[-1] == event and event["type"] == ActivityTypes.KING_GAIN:
            # last thing someone did was become KING
            uid = event["uid"]
            end_time = datetime.datetime.now()
            if end_time > end:
                end_time = end
            timestamp = event["timestamp"]  # type: datetime.datetime
            time_king = (end_time - timestamp).total_seconds()
            if uid not in kings:
                kings[uid] = 0
            kings[uid] += time_king

        longest_king = sorted(kings, key=lambda x: kings[x], reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=longest_king,
            award=AwardsTypes.LONGEST_KING,
            month=start.strftime("%b %y"),
            value=int(kings[longest_king]),
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="longest_king",
            annual=self.annual,
        )

        data_class.kings = {str(k): v for k, v in kings.items()}
        return self.add_annual_changes(start, data_class)

    # vc
    def big_gamer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who spent the most time in VC.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period.

        Returns:
            Stat: the VC stat
        """
        vc_interactions = self.cache.get_vc_interactions(guild_id, start, end)

        user_dict = {}
        for vc in vc_interactions:
            user_id = vc["user_id"]
            channel_id = vc["channel_id"]

            if user_id not in user_dict:
                user_dict[user_id] = {"count": 0, "channels": []}

            user_dict[user_id]["count"] += vc["time_in_vc"]
            if channel_id not in user_dict[user_id]["channels"]:
                user_dict[user_id]["channels"].append(channel_id)

        try:
            big_gamer = sorted(user_dict, key=lambda x: user_dict[x]["count"], reverse=True)[0]
        except IndexError:
            big_gamer = 0
            user_dict[0] = {"count": 0, "channels": {}}

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=big_gamer,
            award=AwardsTypes.BIG_GAMER,
            month=start.strftime("%b %y"),
            value=int(user_dict[big_gamer]["count"]),
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="big_gamer",
            annual=self.annual,
        )

        data_class.users = {str(k): v for k, v in user_dict.items()}
        data_class.channels = len(user_dict[big_gamer]["channels"])
        return self.add_annual_changes(start, data_class)

    def big_streamer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who spent the most time streaming.

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period.

        Returns:
            Stat: the award
        """
        vc_interactions = self.cache.get_vc_interactions(guild_id, start, end)

        user_dict = {}
        for vc in vc_interactions:
            user_id = vc["user_id"]
            channel_id = vc["channel_id"]

            if user_id not in user_dict:
                user_dict[user_id] = {"count": 0, "channels": []}

            user_dict[user_id]["count"] += vc["time_streaming"]
            if channel_id not in user_dict[user_id]["channels"] and vc["time_streaming"]:
                user_dict[user_id]["channels"].append(channel_id)

        try:
            big_streamer = sorted(user_dict, key=lambda x: user_dict[x]["count"], reverse=True)[0]
        except IndexError:
            big_streamer = BSE_BOT_ID
            user_dict[BSE_BOT_ID] = {"count": 0, "channels": {}}

        if user_dict[big_streamer]["count"] == 0 and big_streamer != BSE_BOT_ID:
            # make the bot win if no-one streamed
            big_streamer = BSE_BOT_ID
            user_dict[BSE_BOT_ID] = {"count": 0, "channels": {}}

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=big_streamer,
            award=AwardsTypes.BIG_STREAMER,
            month=start.strftime("%b %y"),
            value=int(user_dict[big_streamer]["count"]),
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="big_streamer",
            annual=self.annual,
        )

        data_class.users = {str(k): v for k, v in user_dict.items()}
        data_class.channels = len(user_dict[big_streamer]["channels"])
        return self.add_annual_changes(start, data_class)
