"""Stats data cache."""

import datetime

from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.transactions import UserTransactions
from mongo.datatypes.bet import BetDB
from mongo.datatypes.customs import EmojiDB
from mongo.datatypes.datatypes import ActivityDB, TransactionDB
from mongo.datatypes.message import MessageDB, VCInteractionDB
from mongo.datatypes.user import UserDB


class StatsDataCache:
    """Class for stats data cache."""

    _cache_time = 3600

    def __init__(self, annual: bool = False, uid: int | None = None) -> None:
        """Initialisation method.

        Args:
            annual (bool, optional): whether to gather annual or monthly stats. Defaults to False.
            uid (int | None, optional): the user ID. Defaults to None.
        """
        self.user_bets = UserBets()
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.threads = SpoilerThreads()
        self.trans = UserTransactions()
        self.activities = UserActivities()

        self.annual = annual

        self.__start_cache: datetime.datetime | None = None
        self.__end_cache: datetime.datetime | None = None
        self.__user_id_cache: int | None = uid

        self.__message_cache: list[MessageDB] = []
        self.__message_cache_time: datetime.datetime | None = None

        self.__vc_cache: list[VCInteractionDB] = []
        self.__vc_cache_time: datetime.datetime | None = None

        self.__bet_cache: list[BetDB] = []
        self.__bet_cache_time: datetime.datetime | None = None

        self.__user_cache: list[UserDB] = []
        self.__user_cache_time: datetime.datetime | None = None

        self.__transaction_cache: list[TransactionDB] = []
        self.__transaction_cache_time: datetime.datetime | None = None

        self.__activity_cache: list[ActivityDB] = []
        self.__activity_cache_time: datetime.datetime | None = None

        self.__reactions_cache: list[MessageDB] = []
        self.__reactions_cache_time: datetime.datetime | None = None

        self.__emoji_cache: list[EmojiDB] = []
        self.__emoji_cache_time: datetime.datetime | None = None

        self.__reply_cache: list[MessageDB] = []
        self.__reply_cache_time: datetime.datetime | None = None

        self.__edit_cache: list[MessageDB] = []
        self.__edit_cache_time: datetime.datetime | None = None

    # caching functions
    def get_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Internal method to query for messages between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__message_cache and (now - self.__message_cache_time).total_seconds() < self._cache_time:
            return self.__message_cache

        self.__message_cache = self.user_interactions.paginated_query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "is_bot": {"$ne": True},
            },
        )

        if self.__user_id_cache:
            self.__message_cache = [m for m in self.__message_cache if m.user_id == self.__user_id_cache]

        self.__message_cache_time = now
        return self.__message_cache

    def get_edited_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Internal method to query for edited messages between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__edit_cache and (now - self.__edit_cache_time).total_seconds() < self._cache_time:
            return self.__edit_cache

        self.__edit_cache = self.user_interactions.paginated_query(
            {
                "guild_id": guild_id,
                "edited": {"$gt": start, "$lt": end},
                "edit_count": {"$gte": 1},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "is_bot": {"$ne": True},
            },
        )

        if self.__user_id_cache:
            self.__edit_cache = [m for m in self.__edit_cache if m.user_id == self.__user_id_cache]

        self.__edit_cache_time = now
        return self.__edit_cache

    def get_vc_interactions(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> list[VCInteractionDB]:
        """Internal method to query for VC interactions between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__vc_cache and (now - self.__vc_cache_time).total_seconds() < self._cache_time:
            return self.__vc_cache

        self.__vc_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}, "message_type": "vc_joined"},
        )

        if self.__user_id_cache:
            self.__vc_cache = [m for m in self.__vc_cache if m.user_id == self.__user_id_cache]

        self.__vc_cache_time = now
        return self.__vc_cache

    def get_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[BetDB]:
        """Internal method to query for bets between a certain date.

        Will cache the bets on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__bet_cache and (now - self.__bet_cache_time).total_seconds() < self._cache_time:
            return self.__bet_cache

        self.__bet_cache = self.user_bets.query(
            {"guild_id": guild_id, "created": {"$gt": start, "$lt": end}},
            limit=10000,
        )
        self.__bet_cache_time = now
        return self.__bet_cache

    def get_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[UserDB]:
        """Internal method to query for users.

        Will cache the users on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID to get users for

        Returns:
            list: list of users dicts
        """
        now = datetime.datetime.now()

        if start != self.__start_cache or end != self.__end_cache:
            self.__user_cache = []

        if self.__user_cache and (now - self.__user_cache_time).total_seconds() < self._cache_time:
            return self.__user_cache

        self.__user_cache = self.user_points.query({"guild_id": guild_id})
        self.__user_cache_time = now
        return self.__user_cache

    def get_transactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[TransactionDB]:
        """Internal method to query for transactions between a certain date.

        Will cache the transactions on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__transaction_cache and (now - self.__transaction_cache_time).total_seconds() < self._cache_time:
            return self.__transaction_cache

        _transactions = self.trans.get_guild_transactions_by_timestamp(guild_id, start, end)
        if self.__user_id_cache:
            _transactions = [t for t in _transactions if t["uid"] == self.__user_id_cache]
        self.__transaction_cache = _transactions
        self.__transaction_cache_time = now
        return self.__transaction_cache

    def get_activities(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[ActivityDB]:
        """Internal method to query for activities between a certain date.

        Will cache the activities on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__activity_cache and (now - self.__activity_cache_time).total_seconds() < self._cache_time:
            return self.__activity_cache

        _activities = self.activities.get_guild_activities_by_timestamp(guild_id, start, end)
        if self.__user_id_cache:
            _activities = [a for a in _activities if a["uid"] == self.__user_id_cache]
        self.__activity_cache = _activities
        self.__activity_cache_time = now
        return self.__activity_cache

    def get_reactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Internal method to query for messages between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__reactions_cache and (now - self.__reactions_cache_time).total_seconds() < self._cache_time:
            return self.__reactions_cache

        self.__reactions_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "reactions.timestamp": {"$gt": start, "$lt": end}},
        )

        self.__reactions_cache_time = now
        return self.__reactions_cache

    def get_emojis(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[EmojiDB]:
        """Internal method to query for server emojis.

        Will cache the emojis on first parse and return the cache if cache was set less than an hour ago.

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

        if self.__emoji_cache and (now - self.__emoji_cache_time).total_seconds() < self._cache_time:
            return self.__emoji_cache

        self.__emoji_cache = self.server_emojis.get_all_emojis(guild_id)
        self.__emoji_cache_time = now
        return self.__emoji_cache

    def get_threaded_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """_summary_.

        Args:
            guild_id (int): the guild ID to get threads for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            List[Message]: list of messages
        """
        all_messages = self.get_messages(guild_id, start, end)
        return [mes for mes in all_messages if mes.is_thread]

    def get_replies(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """_summary_.

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

        if self.__reply_cache and (now - self.__reply_cache_time).total_seconds() < self._cache_time:
            return self.__reply_cache

        self.__reply_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "replies.timestamp": {"$gt": start, "$lt": end}},
        )

        self.__reply_cache_time = now
        return self.__reply_cache
