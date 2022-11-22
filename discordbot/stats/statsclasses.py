
import datetime
import re
from copy import deepcopy
from typing import Tuple

from discordbot.bot_enums import ActivityTypes, AwardsTypes, StatTypes, TransactionTypes
from discordbot.constants import ANNUAL_AWARDS_AWARD, BSE_BOT_ID, JERK_OFF_CHAT, MONTHLY_AWARDS_PRIZE
from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.stats.statsdataclasses import Stat


class StatsGatherer:
    def __init__(self, logger, annual: bool = False) -> None:
        self.annual = annual
        self.logger = logger
        self.cache = StatsDataCache(self.annual)

    @staticmethod
    def get_monthly_datetime_objects() -> Tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous month

        Returns:
            Tuple[datetime.datetime, datetime.datetime]:
        """
        now = datetime.datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
        try:
            start = start.replace(month=start.month - 1)
        except ValueError:
            start = start.replace(month=12)

        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
        return start, end

    @staticmethod
    def get_annual_datetime_objects() -> Tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous year

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
        """Adds changes for annual mode

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
        """Returns the number of messages between two given time periods

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: the number of messages
        """
        messages = self.cache.get_messages(guild_id, start, end)

        channel_ids = set([m["channel_id"] for m in messages])
        user_ids = set([m["user_id"] for m in messages])

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.NUMBER_OF_MESSAGES,
            month=start.strftime("%b %y"),
            value=len(messages),
            timestamp=datetime.datetime.now(),
            short_name="number_of_messages",
            annual=self.annual
        )

        data_class.channels = len(channel_ids)
        data_class.users = len(user_ids)
        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def average_message_length(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[Stat]:
        """Returns the average message length between two given time periods
        Returns a tuple of (AVERAGE_CHARACTERs, AVERAGE_WORDs)

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Tuple[Stat, Stat]: returns a tuple of average message characters and average words per message
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
            annual=self.annual
        )

        data_class_b = Stat(
            "stat",
            guild_id,
            stat=StatTypes.AVERAGE_MESSAGE_LENGTH_WORDS,
            month=start.strftime("%b %y"),
            value=average_word_number,
            timestamp=datetime.datetime.now(),
            short_name="average_message_length_words",
            annual=self.annual
        )

        data_class_a = self.add_annual_changes(start, data_class_a)
        data_class_b = self.add_annual_changes(start, data_class_b)

        return data_class_a, data_class_b

    def busiest_channel(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the channel with the most messages for a given time period
        Returns a float of the channel ID and the number of messages

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Tuple[int, int]: float of channel ID and number of messages
        """
        messages = self.cache.get_messages(guild_id, start, end)

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
            annual=self.annual
        )

        data_class.messages = channels[busiest]["count"]
        data_class.users = len(channels[busiest]["users"])
        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def busiest_thread(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """_summary_

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Stat: _description_
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

        busiest = sorted(threads, key=lambda x: threads[x]["count"], reverse=True)[0]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.BUSIEST_THREAD,
            month=start.strftime("%b %y"),
            value=busiest,
            timestamp=datetime.datetime.now(),
            short_name="busiest_thread",
            annual=self.annual
        )
        data_class.messages = threads[busiest]["count"]
        data_class.users = len(threads[busiest]["users"])
        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def busiest_day(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the day with the most messages sent for the given time period
        Returns a tuple of the date and number of messages

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period

        Returns:
            Tuple[datetime.date, int]: The date with most messages and the number of messages
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
            annual=self.annual
        )

        data_class.messages = days[busiest]["count"]
        data_class.channels = len(days[busiest]["channels"])
        data_class.users = len(days[busiest]["users"])
        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def number_of_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the number of bets between two given time periods

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: the number of bets
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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def salary_gains(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the total amount of eddies gained through salaries this month

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: _description_
        """
        transactions = self.cache.get_transactions(guild_id, start, end)
        salary_total = 0
        for trans in transactions:
            if trans["type"] != TransactionTypes.DAILY_SALARY:
                continue
            salary_total += trans["amount"]

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.SALARY_GAINS,
            month=start.strftime("%b %y"),
            value=salary_total,
            timestamp=datetime.datetime.now(),
            short_name="salary_total",
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def average_wordle_victory(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the server's average wordle score

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            float: The average wordle score
        """
        messages = self.cache.get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]

        wordle_count = []
        for wordle in wordle_messages:
            if wordle["user_id"] == BSE_BOT_ID:
                continue

            result = re.search(r"\d/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "10"
            guesses = int(guesses)
            wordle_count.append(guesses)

        average_wordle = round((sum(wordle_count) / len(wordle_count)), 2)

        data_class = Stat(
            "stat",
            guild_id,
            stat=StatTypes.AVERAGE_WORDLE_VICTORY,
            month=start.strftime("%b %y"),
            value=average_wordle,
            timestamp=datetime.datetime.now(),
            short_name="average_wordle_victory",
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def bet_eddies_stats(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[Stat, Stat]:
        """Calculates the total eddies placed on bets, and the total eddies won on bets

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: returns a tuple of eddies placed and eddies won
        """
        transactions = self.cache.get_transactions(guild_id, start, end)

        eddies_placed = 0
        eddies_won = 0
        for trans in transactions:
            trans_type = trans["type"]
            if trans_type == TransactionTypes.BET_PLACE:
                eddies_placed -= trans["amount"]  # amount is negative in these cases
            elif trans_type == TransactionTypes.BET_WIN:
                eddies_won += trans["amount"]

        data_class_a = Stat(
            "stat",
            guild_id,
            stat=StatTypes.EDDIES_PLACED,
            month=start.strftime("%b %y"),
            value=eddies_placed,
            timestamp=datetime.datetime.now(),
            short_name="number_of_eddies_placed",
            annual=self.annual
        )

        data_class_b = Stat(
            "stat",
            guild_id,
            stat=StatTypes.EDDIES_WIN,
            month=start.strftime("%b %y"),
            value=eddies_won,
            timestamp=datetime.datetime.now(),
            short_name="number_of_eddies_won",
            annual=self.annual
        )

        data_class_a = self.add_annual_changes(start, data_class_a)
        data_class_b = self.add_annual_changes(start, data_class_b)

        return data_class_a, data_class_b

    def most_unique_channel_contributers(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the channel with the most unique contributors

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )

        data_class.users = len(channels[most_popular_channel])

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def total_time_spent_in_vc(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the total amount of time spent by everyone in all VCs

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )

        data_class.users = len(users)
        data_class.channels = len(channels)

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def vc_with_most_time_spent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which VC had the most time spent in it

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )

        data_class.users = len(channels[vc_most_time]["users"])
        data_class.time = int(channels[vc_most_time]["count"])

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def vc_with_most_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which VC had the most unique users in it

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )
        data_class.time = int(channels[vc_most_users]["count"])
        data_class.users = len(channels[vc_most_users]["users"])

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def most_popular_server_emoji(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the most popular server emoji for the given time frame

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: the ServerEmoji data class
        """

        reaction_messages = self.cache.get_reactions(guild_id, start, end)
        messages = self.cache.get_messages(guild_id, start, end)

        reactions = []
        for react in reaction_messages:
            reactions.extend(react["reactions"])

        all_emojis = self.cache.get_emojis(guild_id, start, end)
        all_emoji_names = [emoji["name"] for emoji in all_emojis]

        emoji_count = {}
        for reaction in reactions:
            content = reaction["content"]
            if content not in all_emoji_names:
                continue
            if content not in emoji_count:
                emoji_count[content] = 0
            emoji_count[content] += 1

        for message in messages:
            for emoji_name in all_emoji_names:
                if emojis := re.findall(f":{emoji_name}:", message["content"]):
                    if emoji_name not in emoji_count:
                            emoji_count[emoji_name] = 0
                    emoji_count[emoji_name] += len(emojis)

        most_used_emoji = sorted(emoji_count, key=lambda x: emoji_count[x], reverse=True)[0]

        emoji_id = [emoji["eid"] for emoji in all_emojis if emoji["name"] == most_used_emoji][0]

        data_class = Stat(
            type="stat",
            guild_id=guild_id,
            stat=StatTypes.MOST_POPULAR_SERVER_EMOJI,
            month=start.strftime("%b %y"),
            value=most_used_emoji,
            timestamp=datetime.datetime.now(),
            short_name="most_used_server_emoji",
            annual=self.annual
        )

        data_class.count = emoji_count[most_used_emoji]
        data_class.emoji_id = emoji_id

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    # stats that can be won
    # messages
    def most_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the person who has sent the most messages in the server

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
                message_users[uid] = 0
            message_users[uid] += 1
        chattiest = sorted(message_users, key=lambda x: message_users[x], reverse=True)[0]

        data_class = Stat(
            type="award",
            guild_id=guild_id,
            user_id=chattiest,
            award=AwardsTypes.MOST_MESSAGES,
            month=start.strftime("%b %y"),
            value=message_users[chattiest],
            timestamp=datetime.datetime.now(),
            eddies=MONTHLY_AWARDS_PRIZE,
            short_name="most_messages_sent",
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def least_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates the person who has sent the least messages in the server

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
        least_chattiest = sorted(message_users, key=lambda x: message_users[x])[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def longest_message(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Returns the longest message from two given time periods

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def lowest_average_wordle_score(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates which user has the best average wordle score

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

            result = re.search(r"\d/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "7"
            guesses = int(guesses)

            wordle_count[uid].append(guesses)

        worlde_count_old = deepcopy(wordle_count)
        for uid in worlde_count_old:
            if len(worlde_count_old[uid]) < threshold:
                # user hasn't done enough wordles in this time period to be
                # counted
                print(
                    f"Removing {uid} from wordle pool as they've only done {len(wordle_count[uid])} wordles."
                )
                wordle_count.pop(uid)

        wordle_avgs = {}
        for uid in wordle_count:
            all_guesses = wordle_count[uid]
            avg = round((sum(all_guesses) / len(all_guesses)), 2)
            wordle_avgs[uid] = avg

        best_avg = sorted(wordle_avgs, key=lambda x: wordle_avgs[x])[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    # bets
    def most_bets_created(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Get the user who made the most bets

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
            u = bet["user"]
            if u not in bet_users:
                bet_users[u] = 0
            bet_users[u] += 1

        busiest = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def most_eddies_bet(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who placed the most eddies on bets

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
            if trans["type"] != TransactionTypes.BET_PLACE:
                continue
            uid = trans["uid"]
            if uid not in bet_users:
                bet_users[uid] = 0
            bet_users[uid] -= trans["amount"]

        most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def most_eddies_won(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who won the most eddies on bets

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
            if trans["type"] != TransactionTypes.BET_WIN:
                continue
            uid = trans["uid"]
            if uid not in bet_users:
                bet_users[uid] = 0
            bet_users[uid] += trans["amount"]

        most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def most_time_king(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's been King longest this month

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: longest King stat
        """

        activity_history = self.cache.get_activities(guild_id, start, end)
        king_events = sorted(
            [a for a in activity_history if a["type"] in [ActivityTypes.KING_GAIN, ActivityTypes.KING_LOSS]],
            key=lambda x: x["timestamp"]
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
            # this section is the worst
            try:
                end_time = start.replace(day=31, hour=23, minute=59, second=59)
            except ValueError:
                try:
                    end_time = start.replace(day=30, hour=23, minute=59, second=59)
                except ValueError:
                    try:
                        end_time = start.replace(day=29, hour=23, minute=59, second=59)
                    except ValueError:
                        end_time = start.replace(day=28, hour=23, minute=59, second=59)
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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def twitter_addict(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's posted the most twitter links

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
            if "twitter" in message["content"] and "link" in message["message_type"]:
                user_id = message["user_id"]
                if user_id not in tweet_users:
                    tweet_users[user_id] = 0
                tweet_users[user_id] += 1

        twitter_addict = sorted(tweet_users, key=lambda x: tweet_users[x], reverse=True)[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def jerk_off_contributor(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """Calculates who's posted this most contributions in #jerk-off-chat

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
        """
        messages = self.cache.get_messages(guild_id, start, end)
        jerk_off_messages = [m for m in messages if m["channel_id"] == JERK_OFF_CHAT]

        jerk_off_users = {}
        for message in jerk_off_messages:
            if any([a for a in ["link", "attachment"] if a in message["message_type"]]):
                user_id = message["user_id"]
                if user_id not in jerk_off_users:
                    jerk_off_users[user_id] = 0
                jerk_off_users[user_id] += 1

        masturbator = sorted(jerk_off_users, key=lambda x: jerk_off_users[x], reverse=True)[0]

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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def big_memer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def react_king(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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
            annual=self.annual
        )

        data_class = self.add_annual_changes(start, data_class)

        return data_class

    # vc
    def big_gamer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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

        big_gamer = sorted(user_dict, key=lambda x: user_dict[x]["count"], reverse=True)[0]

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
            annual=self.annual
        )

        data_class.channels = len(user_dict[big_gamer]["channels"])
        data_class = self.add_annual_changes(start, data_class)

        return data_class

    def big_streamer(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Stat:
        """

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Stat: _description_
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

        big_streamer = sorted(user_dict, key=lambda x: user_dict[x]["count"], reverse=True)[0]

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
            annual=self.annual
        )

        data_class.channels = len(user_dict[big_streamer]["channels"])
        data_class = self.add_annual_changes(start, data_class)

        return data_class
