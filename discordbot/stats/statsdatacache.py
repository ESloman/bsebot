
import datetime
from typing import List, Optional

from mongo.bsepoints import UserBets, UserInteractions, UserPoints


class StatsDataCache:
    def __init__(self, annual: bool = False) -> None:
        self.user_bets = UserBets()
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()

        self.annual = annual

        self.__start_cache = None  # type: Optional[datetime.datetime]
        self.__end_cache = None  # type: Optional[datetime.datetime]

        self.__message_cache = []  # type: List[dict]
        self.__message_cache_time = None  # type: Optional[datetime.datetime]

        self.__vc_cache = []  # type: List[dict]
        self.__vc_cache_time = None  # type: Optional[datetime.datetime]

        self.__bet_cache = []  # type: List[dict]
        self.__bet_cache_time = None  # type: Optional[datetime.datetime]

        self.__user_cache = []  # type: List[dict]
        self.__user_cache_time = None  # type: Optional[datetime.datetime]

        self.__transaction_cache = []  # type: List[dict]
        self.__transaction_cache_time = None  # type: Optional[datetime.datetime]

        self.__activity_cache = []  # type: List[dict]
        self.__activity_cache_time = None  # type: Optional[datetime.datetime]

        self.__reactions_cache = []  # type: List[dict]
        self.__reactions_cache_time = None  # type: Optional[datetime.datetime]

    # caching functions
    def get_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
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

        if start != self.__start_cache or end != self.__end_cache:
            self.__message_cache = []

        if self.__message_cache and (now - self.__message_cache_time).total_seconds() < 3600:
            return self.__message_cache

        limit = 100000 if self.annual else 10000

        self.__message_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]}
            },
            limit=limit
        )

        self.__message_cache_time = now
        return self.__message_cache

    def get_vc_interactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for VC interactions between a certain date
        Will cache the messages on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get messages for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list: list of message dicts
        """
        now = datetime.datetime.now()

        if start != self.__start_cache or end != self.__end_cache:
            self.__vc_cache = []

        if self.__vc_cache and (now - self.__vc_cache_time).total_seconds() < 3600:
            return self.__vc_cache

        limit = 100000 if self.annual else 10000

        self.__vc_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": "vc_joined"
            },
            limit=limit
        )

        self.__vc_cache_time = now
        return self.__vc_cache

    def get_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
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

        if start != self.__start_cache or end != self.__end_cache:
            self.__bet_cache = []

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

    def get_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
        """Internal method to query for users
        Will cache the users on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get users for

        Returns:
            list: list of users dicts
        """
        now = datetime.datetime.now()

        if start != self.__start_cache or end != self.__end_cache:
            self.__user_cache = []

        if self.__user_cache and (now - self.__user_cache_time).total_seconds() < 3600:
            return self.__user_cache

        self.__user_cache = self.user_points.query({"guild_id": guild_id})
        self.__user_cache_time = now
        return self.__user_cache

    def get_transactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
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

        if start != self.__start_cache or end != self.__end_cache:
            self.__transaction_cache = []

        if self.__transaction_cache and (now - self.__transaction_cache_time).total_seconds() < 3600:
            return self.__transaction_cache

        users = self.get_users(guild_id, start, end)
        transaction_history = []
        for user in users:
            transactions = [t for t in user.get("transaction_history", []) if start < t["timestamp"] < end]
            for _trans in transactions:
                _trans["uid"] = user["uid"]
            transaction_history.extend(transactions)
        self.__transaction_cache = transaction_history
        self.__transaction_cache_time = now
        return self.__transaction_cache

    def get_activities(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
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

        if start != self.__start_cache or end != self.__end_cache:
            self.__activity_cache = []

        if self.__activity_cache and (now - self.__activity_cache_time).total_seconds() < 3600:
            return self.__activity_cache

        users = self.get_users(guild_id, start, end)
        activity_history = []
        for user in users:
            activities = [t for t in user.get("activity_history", []) if start < t["timestamp"] < end]
            for _act in activities:
                _act["uid"] = user["uid"]
            activity_history.extend(activities)
        self.__activity_cache = activity_history
        self.__activity_cache_time = now
        return self.__activity_cache

    def get_reactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[dict]:
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

        if start != self.__start_cache or end != self.__end_cache:
            self.__reactions_cache = []

        if self.__reactions_cache and (now - self.__reactions_cache_time).total_seconds() < 3600:
            return self.__reactions_cache

        limit = 100000 if self.annual else 10000

        self.__reactions_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "reactions.timestamp": {"$gt": start, "$lt": end}
            },
            limit=limit
        )
        self.__reactions_cache_time = now
        return self.__reactions_cache
