"""Stats data cache."""

import datetime

from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.transactions import UserTransactions
from mongo.datatypes.actions import ActivityDB, TransactionDB
from mongo.datatypes.bet import BetDB
from mongo.datatypes.customs import EmojiDB
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

        self._start_cache: datetime.datetime | None = None
        self._end_cache: datetime.datetime | None = None
        self._user_id_cache: int | None = uid

        self._message_cache: list[MessageDB] = []
        self._message_cache_time: datetime.datetime | None = None

        self._vc_cache: list[VCInteractionDB] = []
        self._vc_cache_time: datetime.datetime | None = None

        self._bet_cache: list[BetDB] = []
        self._bet_cache_time: datetime.datetime | None = None

        self._user_cache: list[UserDB] = []
        self._user_cache_time: datetime.datetime | None = None

        self._transaction_cache: list[TransactionDB] = []
        self._transaction_cache_time: datetime.datetime | None = None

        self._activity_cache: list[ActivityDB] = []
        self._activity_cache_time: datetime.datetime | None = None

        self._reactions_cache: list[MessageDB] = []
        self._reactions_cache_time: datetime.datetime | None = None

        self._emoji_cache: list[EmojiDB] = []
        self._emoji_cache_time: datetime.datetime | None = None

        self._reply_cache: list[MessageDB] = []
        self._reply_cache_time: datetime.datetime | None = None

        self._edit_cache: list[MessageDB] = []
        self._edit_cache_time: datetime.datetime | None = None

    # caching functions
    def get_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Internal method to query for messages between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID to get messages for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list[MessageDB]: list of messages
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._message_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._message_cache and (now - self._message_cache_time).total_seconds() < self._cache_time:
            return self._message_cache

        self._message_cache = self.user_interactions.paginated_query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "is_bot": {"$ne": True},
            },
        )

        if self._user_id_cache:
            self._message_cache = [m for m in self._message_cache if m.user_id == self._user_id_cache]

        self._message_cache_time = now
        return self._message_cache

    def get_edited_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Internal method to query for edited messages between a certain date.

        Will cache the messages on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID to get messages for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list[MessageDB]: list of edited messages
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._edit_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._edit_cache and (now - self._edit_cache_time).total_seconds() < self._cache_time:
            return self._edit_cache

        self._edit_cache = self.user_interactions.paginated_query(
            {
                "guild_id": guild_id,
                "edited": {"$gt": start, "$lt": end},
                "edit_count": {"$gte": 1},
                "message_type": {"$nin": ["emoji_used", "vc_joined", "vc_streaming"]},
                "is_bot": {"$ne": True},
            },
        )

        if self._user_id_cache:
            self._edit_cache = [m for m in self._edit_cache if m.user_id == self._user_id_cache]

        self._edit_cache_time = now
        return self._edit_cache

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
            list[VCInteractionDB]: list of VC interactions
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._vc_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._vc_cache and (now - self._vc_cache_time).total_seconds() < self._cache_time:
            return self._vc_cache

        self._vc_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}, "message_type": "vc_joined"},
        )

        if self._user_id_cache:
            self._vc_cache = [m for m in self._vc_cache if m.user_id == self._user_id_cache]

        self._vc_cache_time = now
        return self._vc_cache

    def get_bets(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[BetDB]:
        """Internal method to query for bets between a certain date.

        Will cache the bets on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID to get bets for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list[BetDB]: list of bets
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._bet_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._bet_cache and (now - self._bet_cache_time).total_seconds() < self._cache_time:
            return self._bet_cache

        self._bet_cache = self.user_bets.query(
            {"guild_id": guild_id, "created": {"$gt": start, "$lt": end}},
            limit=10000,
        )
        self._bet_cache_time = now
        return self._bet_cache

    def get_users(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[UserDB]:
        """Internal method to query for users.

        Will cache the users on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID to get users for

        Returns:
            list[UserDB]: list of users
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._user_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._user_cache and (now - self._user_cache_time).total_seconds() < self._cache_time:
            return self._user_cache

        self._user_cache = self.user_points.query({"guild_id": guild_id})
        self._user_cache_time = now
        return self._user_cache

    def get_transactions(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[TransactionDB]:
        """Internal method to query for transactions between a certain date.

        Will cache the transactions on first parse and return the cache if cache was set less than an hour ago.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): the beginning of time period
            end (datetime.datetime): the end of the time period

        Returns:
            list[TransactionDB]: a list of transactions
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._transaction_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._transaction_cache and (now - self._transaction_cache_time).total_seconds() < self._cache_time:
            return self._transaction_cache

        _transactions = self.trans.get_guild_transactions_by_timestamp(guild_id, start, end)
        if self._user_id_cache:
            _transactions = [t for t in _transactions if t.uid == self._user_id_cache]
        self._transaction_cache = _transactions
        self._transaction_cache_time = now
        return self._transaction_cache

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

        if start != self._start_cache or end != self._end_cache:
            self._activity_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._activity_cache and (now - self._activity_cache_time).total_seconds() < self._cache_time:
            return self._activity_cache

        _activities = self.activities.get_guild_activities_by_timestamp(guild_id, start, end)
        if self._user_id_cache:
            _activities = [a for a in _activities if a.uid == self._user_id_cache]
        self._activity_cache = _activities
        self._activity_cache_time = now
        return self._activity_cache

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

        if start != self._start_cache or end != self._end_cache:
            self._reactions_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._reactions_cache and (now - self._reactions_cache_time).total_seconds() < self._cache_time:
            return self._reactions_cache

        self._reactions_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "reactions.timestamp": {"$gt": start, "$lt": end}},
        )

        self._reactions_cache_time = now
        return self._reactions_cache

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

        if start != self._start_cache or end != self._end_cache:
            self._emoji_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._emoji_cache and (now - self._emoji_cache_time).total_seconds() < self._cache_time:
            return self._emoji_cache

        self._emoji_cache = self.server_emojis.get_all_emojis(guild_id)
        self._emoji_cache_time = now
        return self._emoji_cache

    def get_threaded_messages(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Get the threaded messages from the cache.

        Uses the message cache to get the messages.

        Args:
            guild_id (int): the guild ID to get threads for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list[MessageDB]: list of messages
        """
        all_messages = self.get_messages(guild_id, start, end)
        return [mes for mes in all_messages if mes.is_thread]

    def get_replies(self, guild_id: int, start: datetime.datetime, end: datetime.datetime) -> list[MessageDB]:
        """Gets all the messages with replies.

        Args:
            guild_id (int): the guild ID to get replies for
            start (datetime.datetime): start of timestamp query
            end (datetime.datetime): end of timestamp query

        Returns:
            list[MessageDB]: list of messages
        """
        now = datetime.datetime.now()

        if start != self._start_cache or end != self._end_cache:
            self._reply_cache = []
            self._start_cache = start
            self._end_cache = end

        if self._reply_cache and (now - self._reply_cache_time).total_seconds() < self._cache_time:
            return self._reply_cache

        self._reply_cache = self.user_interactions.paginated_query(
            {"guild_id": guild_id, "replies.timestamp": {"$gt": start, "$lt": end}},
        )

        self._reply_cache_time = now
        return self._reply_cache
