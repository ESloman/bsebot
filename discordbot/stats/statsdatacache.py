
import datetime
# can ignore F401 here - we're using Optional in the type hints in variable declaration
from typing import List, Optional  # noqa: F401

from discordbot.constants import BOT_IDS
from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints import ServerEmojis, UserBets, UserInteractions, UserPoints
from mongo.datatypes import Activity, Bet, Emoji, Message, Reaction, Transaction, User, VCInteraction


class StatsDataCache:
    def __init__(self, annual: bool = False) -> None:
        self.user_bets = UserBets()
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.threads = SpoilerThreads()

        self.annual = annual

        self.__start_cache = None  # type: Optional[datetime.datetime]
        self.__end_cache = None  # type: Optional[datetime.datetime]
        self.__user_id_cache = None  # type: Optional[int]

        self.__message_cache = []  # type: List[Message]
        self.__message_cache_time = None  # type: Optional[datetime.datetime]

        self.__vc_cache = []  # type: List[VCInteraction]
        self.__vc_cache_time = None  # type: Optional[datetime.datetime]

        self.__bet_cache = []  # type: List[Bet]
        self.__bet_cache_time = None  # type: Optional[datetime.datetime]

        self.__user_cache = []  # type: List[User]
        self.__user_cache_time = None  # type: Optional[datetime.datetime]

        self.__transaction_cache = []  # type: List[Transaction]
        self.__transaction_cache_time = None  # type: Optional[datetime.datetime]

        self.__activity_cache = []  # type: List[Activity]
        self.__activity_cache_time = None  # type: Optional[datetime.datetime]

        self.__reactions_cache = []  # type: List[Reaction]
        self.__reactions_cache_time = None  # type: Optional[datetime.datetime]

        self.__emoji_cache = []  # type: List[Emoji]
        self.__emoji_cache_time = None  # type: Optional[datetime.datetime]

        self.__reply_cache = []  # type: List[Message]
        self.__reply_cache_time = None  # type: Optional[datetime.datetime]

        self.__edit_cache = []  # type: List[Message]
        self.__edit_cache_time = None  # type: Optional[datetime.datetime]

    # caching functions
    def get_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Message]:
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

        limit = 100000

        self.__message_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "user_id": {"$nin": BOT_IDS}
            },
            limit=limit
        )

        self.__message_cache_time = now
        return self.__message_cache

    def get_edited_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Message]:
        """Internal method to query for edited messages between a certain date
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
            self.__edit_cache = []

        if self.__edit_cache and (now - self.__edit_cache_time).total_seconds() < 3600:
            return self.__edit_cache

        limit = 2000
        self.__edit_cache = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "edited": {"$gt": start, "$lt": end},
                "edit_count": {"$gte": 1},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "user_id": {"$nin": BOT_IDS}
            },
            limit=limit
        )

        self.__edit_cache_time = now
        return self.__edit_cache

    def get_vc_interactions(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> List[VCInteraction]:
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

    def get_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Bet]:
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

    def get_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[User]:
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

    def get_transactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Transaction]:
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

    def get_activities(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Activity]:
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

    def get_reactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Reaction]:
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

    def get_emojis(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Emoji]:
        """Internal method to query for server emojis
        Will cache the emojis on first parse and return the cache if cache was set less than an hour ago

        Args:
            guild_id (int): the guild ID to get emojis for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list: list of message dicts
        """
        now = datetime.datetime.now()

        if start != self.__start_cache or end != self.__end_cache:
            self.__emoji_cache = []

        if self.__emoji_cache and (now - self.__emoji_cache_time).total_seconds() < 3600:
            return self.__emoji_cache

        self.__emoji_cache = self.server_emojis.get_all_emojis(guild_id)
        self.__emoji_cache_time = now
        return self.__emoji_cache

    def get_threaded_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Message]:
        """_summary_

        Args:
            guild_id (int): the guild ID to get threads for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            List[Message]: list of messages
        """

        all_messages = self.get_messages(guild_id, start, end)
        threaded = [mes for mes in all_messages if mes.get("is_thread")]
        return threaded

    def get_replies(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Message]:
        """_summary_

        Args:
            guild_id (int): the guild ID to get replies for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            List[Message]: _description_
        """

        now = datetime.datetime.now()

        if start != self.__start_cache or end != self.__end_cache:
            self.__reply_cache = []

        if self.__reply_cache and (now - self.__reply_cache_time).total_seconds() < 3600:
            return self.__reply_cache

        self.__reply_cache = self.user_interactions.query({
            "guild_id": guild_id,
            "replies.timestamp": {"$gt": start, "$lt": end}
        })

        self.__reply_cache_time = now
        return self.__reply_cache
