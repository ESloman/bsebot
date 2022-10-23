import datetime
import math
import re
from typing import List, Optional, Tuple

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.constants import BSE_BOT_ID
from mongo.bsepoints import UserBets, UserInteractions, UserPoints


class StatsGatherer:
    def __init__(self) -> None:
        self.user_bets = UserBets()
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()

        self.__message_cache = []  # type: List[dict]
        self.__message_cache_time = None  # type: Optional[datetime.datetime]

        self.__bet_cache = []  # type: List[dict]
        self.__bet_cache_time = None  # type: Optional[datetime.datetime]

        self.__user_cache = []  # type: List[dict]
        self.__user_cache_time = None  # type: Optional[datetime.datetime]
        
        self.__transaction_cache = []  # type: List[dict]
        self.__transaction_cache_time = None  # type: Optional[datetime.datetime]
        
        self.__activity_cache = []  # type: List[dict]
        self.__activity_cache_time = None  # type: Optional[datetime.datetime]
    
    @staticmethod
    def get_monthly_datetime_objects():
        now = datetime.datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
        new_month = ((start.month + 1) % 12) or 12
        end = start.replace(month=new_month)
        return start, end
    
    # caching functions
    def _get_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for messages between a certain date
        Will cache the messages on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get messages for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list: list of message dicts
        """
        now = datetime.datetime.now()
        if self.__message_cache and (now - self.__message_cache_time).total_seconds() < 3600:
            return self.__message_cache
         
        self.__message_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": {"$nin": ["emoji_used"]}
            },
            limit=10000
        )
        self.__message_cache_time = now
        return self.__message_cache
    
    def _get_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for bets between a certain date
        Will cache the bets on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get bets for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list: list of bet dicts
        """
        now = datetime.datetime.now()
        if self.__bet_cache and (now - self.__bet_cache_time).total_seconds() < 3600:
            return self.__bet_cache
         
        self.__bet_cache = self.user_bets.query(
            {
                "guild_id": guild_id,
                "created": {"$gt": start, "$lt": end}
            },
            limit=10000
        )
        self.__bet_cache_time = now
        return self.__bet_cache

    def _get_users(self, guild_id: int) -> List[dict]:
        """Internal method to query for users
        Will cache the users on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get users for

        Returns:
            list: list of users dicts
        """
        now = datetime.datetime.now()
        if self.__user_cache and (now - self.__user_cache_time).total_seconds() < 3600:
            return self.__user_cache
         
        self.__user_cache = self.user_points.query({"guild_id": guild_id})
        self.__user_cache_time = now
        return self.__user_cache


    def _get_transactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for transactions between a certain date
        Will cache the transactions on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): the beginning of time period
            end (datetime.datetime): the end of the time period

        Returns:
            List[dict]: a list of transactions
        """
        now = datetime.datetime.now()
        if self.__transaction_cache and (now - self.__transaction_cache_time).total_seconds() < 3600:
            return self.__transaction_cache
        
        users = self._get_users(guild_id)
        transaction_history = []
        for user in users:
            transactions = [t for t in user.get("transaction_history", []) if start < t["timestamp"] < end]
            for _trans in transactions:
                _trans["uid"] = user["uid"]
            transaction_history.extend(transactions)
        self.__transaction_cache = transaction_history
        self.__transaction_cache_time = now
        return self.__transaction_cache
    
    def _get_activities(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for activities between a certain date
        Will cache the activities on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): the beginning of time period
            end (datetime.datetime): the end of the time period

        Returns:
            List[dict]: a list of activities
        """
        now = datetime.datetime.now()
        if self.__activity_cache and (now - self.__activity_cache_time).total_seconds() < 3600:
            return self.__activity_cache
        
        users = self._get_users(guild_id)
        activity_history = []
        for user in users:
            activities = [t for t in user.get("activity_history", []) if start < t["timestamp"] < end]
            for _act in activities:
                _act["uid"] = user["uid"]
            activity_history.extend(activities)
        self.__activity_cache = activity_history
        self.__activity_cache_time = now
        return self.__activity_cache
    
    # generic server stats
    def number_of_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> int:
        """Returns the number of messages between two given time periods

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: the number of messages
        """
        messages = self._get_messages(guild_id, start, end)
        return len(messages)
    
    def average_message_length(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[float, float]:
        """Returns the average message length between two given time periods
        Returns a tuple of (AVERAGE_CHARACTERs, AVERAGE_WORDs)

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period 

        Returns:
            Tuple[float, float]: returns a tuple of average message characters and average words per message
        """

        messages = self._get_messages(guild_id, start, end)
        lengths = []
        words = []
        for message in messages:
            if content := message["content"]:
                lengths.append(len(content))
                words.append(len(content.split(" ")))
        average_message_len = round((sum(lengths) / len(lengths)), 2)
        average_word_number = round((sum(words) / len(words)), 2)
        return average_message_len, average_word_number

    def busiest_channel(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Returns the channel with the most messages for a given time period
        Returns a float of the channel ID and the number of messages

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period 

        Returns:
            Tuple[int, int]: float of channel ID and number of messages
        """
        messages = self._get_messages(guild_id, start, end)

        channels = {}
        for message in messages:
            channel_id = message["channel_id"]
            if not channel_id:
                continue
            if channel_id not in channels:
                channels[channel_id] = 0
            channels[channel_id] += 1
        
        busiest = sorted(channels, key=lambda x: channels[x], reverse=True)[0]

        return busiest, channels[busiest]
    
    def busiest_day(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[datetime.date, int]:
        """Returns the day with the most messages sent for the given time period
        Returns a tuple of the date and number of messages

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): beginning of the time period
            end (datetime.datetime): end of the time period 

        Returns:
            Tuple[datetime.date, int]: The date with most messages and the number of messages
        """
        messages = self._get_messages(guild_id, start, end)
        days = {}
        for message in messages:
            day = message["timestamp"].date()
            if day not in days:
                days[day] = 0
            days[day] += 1
        
        busiest = sorted(days, key=lambda x: days[x], reverse=True)[0]
        return busiest, days[busiest]
    
    def number_of_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> int:
        """Returns the number of bets between two given time periods

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: the number of bets
        """
        bets = self._get_bets(guild_id, start, end)
        return len(bets)
    
    def salary_gains(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> int:
        """Returns the total amount of eddies gained through salaries this month

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            int: _description_
        """
        transactions = self._get_transactions(guild_id, start, end)
        salary_total = 0
        for trans in transactions:
            if trans["type"] != TransactionTypes.DAILY_SALARY:
                continue
            salary_total += trans["amount"]
        return salary_total
        
    def average_wordle_victory(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> float:
        """Calculates the server's average wordle score

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            float: The average wordle score
        """
        messages = self._get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]
        
        wordle_count = []
        for wordle in wordle_messages:
            if wordle["user_id"] == BSE_BOT_ID:
                continue
            
            result = re.search("\d\/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "10"
            guesses = int(guesses)
            wordle_count.append(guesses)
            
        average_wordle = round((sum(wordle_count) / len(wordle_count)), 2)
        return average_wordle
    
    def bet_eddies_stats(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Calculates the total eddies placed on bets, and the total eddies won on bets

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: returns a tuple of eddies placed and eddies won
        """
        transactions = self._get_transactions(guild_id, start, end)

        eddies_placed = 0
        eddies_won = 0
        for trans in transactions:
            trans_type = trans["type"]
            if trans_type == TransactionTypes.BET_PLACE:
                eddies_placed -= trans["amount"]  # amount is negative in these cases
            elif trans_type == TransactionTypes.BET_WIN:
                eddies_won += trans["amount"]

        return eddies_placed, eddies_won

    # stats that can be won
    # messages
    def most_messages_sent(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Calculates the person who has sent the most messages in the server

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: the ID of the user and the amount of messages sent
        """
        messages = self._get_messages(guild_id, start, end)

        message_users = {}
        for message in messages:
            uid = message["user_id"]
            if uid not in message_users:
                message_users[uid] = 0
            message_users[uid] += 1
        chattiest = sorted(message_users, key=lambda x: message_users[x], reverse=True)[0]
        return chattiest, message_users[chattiest]

    def longest_message(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> dict:
        """Returns the longest message from two given time periods

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            dict: the longest message dict
        """
        messages = self._get_messages(guild_id, start, end)
        longest_message = None
        for message in messages:
            if content := message["content"]:
                if not longest_message:
                    longest_message = message
                    continue
                if len(content) > len(longest_message["content"]):
                    longest_message = message
        return longest_message

    def lowest_average_wordle_score(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, float]:
        """Calculates which user has the best average wordle score

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, float]: the user ID and the average wordle score
        """
        messages = self._get_messages(guild_id, start, end)
        wordle_messages = [m for m in messages if "wordle" in m["message_type"]]
        
        wordle_count = {}
        for wordle in wordle_messages:
            uid = wordle["user_id"]
            if uid == BSE_BOT_ID:
                continue
            if uid not in wordle_count:
                wordle_count[uid] = []

            result = re.search("\d\/\d", wordle["content"]).group()
            guesses = result.split("/")[0]

            if guesses == "X":
                guesses = "10"
            guesses = int(guesses)

            wordle_count[uid].append(guesses)
        
        wordle_avgs = {}
        for uid in wordle_count:
            all_guesses = wordle_count[uid]
            avg = round((sum(all_guesses) / len(all_guesses)), 2)
            wordle_avgs[uid] = avg
        
        best_avg = sorted(wordle_avgs, key=lambda x: wordle_avgs[x])[0]
        return best_avg, wordle_avgs[best_avg]

    # bets
    def most_bets_created(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Get the user who made the most bets

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: User who created the most bets, number of bets created
        """
        bets = self._get_bets(guild_id, start, end)
        bet_users = {}
        for bet in bets:
            u = bet["user"]
            if u not in bet_users:
                bet_users[u] = 0
            bet_users[u] += 1
        
        busiest = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        return busiest, bet_users[busiest]

    def most_eddies_bet(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Calculates who placed the most eddies on bets

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: User who placed the most bets, the amount they placed
        """
        transactions = self._get_transactions(guild_id, start, end)
        
        bet_users = {}
        for trans in transactions:
            if trans["type"] != TransactionTypes.BET_PLACE:
                continue
            uid = trans["uid"]
            if uid not in bet_users:
                bet_users[uid] = 0
            bet_users[uid] -= trans["amount"]
        
        most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        return most_placed, bet_users[most_placed]
    
    def most_eddies_won(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, float]:
        """Calculates who won the most eddies on bets

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: User who won the most bets, the amount they placed
        """
        transactions = self._get_transactions(guild_id, start, end)
        
        bet_users = {}
        for trans in transactions:
            if trans["type"] != TransactionTypes.BET_WIN:
                continue
            uid = trans["uid"]
            if uid not in bet_users:
                bet_users[uid] = 0
            bet_users[uid] += trans["amount"]
        
        most_placed = sorted(bet_users, key=lambda x: bet_users[x], reverse=True)[0]
        return most_placed, bet_users[most_placed]
    
    def most_time_king(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> Tuple[int, int]:
        """Calculates who's been King longest this month

        Args:
            guild_id (int): the guild ID to query for
            start (datetime.datetime): beginning of time period
            end (datetime.datetime): end of time period

        Returns:
            Tuple[int, int]: User ID of who's been King longest and total seconds they've been King
        """
        
        activity_history = self._get_activities(guild_id, start, end)
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
                
        longest_king = sorted(kings, key=lambda x: kings[x], reverse=True)[0]
        
        return longest_king, int(kings[longest_king])
