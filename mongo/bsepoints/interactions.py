import datetime
from typing import Optional

from mongo import interface
from mongo.datatypes import Message
from mongo.db_classes import BestSummerEverPointsDB


class UserInteractions(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userinteractions' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method for the class. Initialises the collection object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "userinteractions")

    def _paginated_query(self, query_dict: dict) -> list[Message]:
        """Performs a paginated query with the specified query dict

        Args:
            query_dict (dict): a dict of query operators

        Returns:
            list[Message]: a list of messages for the given query
        """
        _lim = 10000
        messages = []
        len_messages_ret = _lim
        skip = 0
        while len_messages_ret == _lim:
            # keep looping
            _messages = self.query(query_dict, limit=_lim, skip=skip)
            skip += _lim
            len_messages_ret = len(_messages)
            messages.extend(_messages)
        return messages

    def get_all_messages_for_server(self, guild_id: int) -> list[Message]:
        """Gets all messages for a given server

        Args:
            guild_id (int): the server Id to get messages for

        Returns:
            list[Message]: list of messages
        """
        messages = self._paginated_query({"guild_id": guild_id})
        return messages

    def get_all_messages_for_channel(self, guild_id: int, channel_id: int) -> list[Message]:
        """Gets all messages for a given channel and guild

        Args:
            guild_id (int): the server Id to get messages for
            channel_id (int): the channel Id to get messages for

        Returns:
            list[Message]: list of messages
        """
        messages = self._paginated_query({"guild_id": guild_id, "channel_id": channel_id})
        return messages

    def add_entry(
            self,
            message_id: int,
            guild_id: int,
            user_id: int,
            channel_id: int,
            message_type: list,
            message_content: str,
            timestamp: datetime.datetime,
            additional_keys: Optional[dict] = None,
            is_thread: Optional[bool] = False,
            is_vc: Optional[bool] = False,
    ) -> None:
        """
        Adds an entry into our interactions DB with the corresponding message.
        :param message_id: int - message ID
        :param guild_id: int - guild ID
        :param user_id: int - user ID
        :param channel_id: int - channel ID
        :param message_type: str - message type
        :param message_content: str - message content
        :param timestamp: - datetime object
        :param additional_keys:
        :param is_thread: whether the entry happened in a thread or not
        :param is_vc: whether the entry happened in a vc or not
        :return: None
        """

        message = {
            "message_id": message_id,
            "guild_id": guild_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "message_type": message_type,
            "content": message_content,
            "timestamp": timestamp,
            "is_thread": is_thread,
            "is_vc": is_vc
        }

        if additional_keys:
            message.update(additional_keys)

        self.insert(message)

    def add_reply_to_message(
            self,
            reference_message_id: int,
            message_id: int,
            guild_id: int,
            user_id: int,
            timestamp: datetime.datetime,
            content: str,
    ):
        """

        :param reference_message_id:
        :param guild_id:
        :param user_id:
        :param message_id:
        :param timestamp:
        :param content:
        :return:
        """
        entry = {
            "user_id": user_id,
            "content": content,
            "timestamp": timestamp,
            "message_id": message_id,
        }

        self.update(
            {"message_id": reference_message_id, "guild_id": guild_id},
            {"$push": {"replies": entry}},
        )

    def add_reaction_entry(
            self,
            message_id: int,
            guild_id: int,
            user_id: int,
            channel_id: int,
            message_content: str,
            timestamp: datetime.datetime,
            author_id: int) -> None:
        """
        Adds a reaction entry into our interactions DB with the corresponding message.
        :param message_id: int - message ID
        :param guild_id: int - guild ID
        :param user_id: int - user ID
        :param channel_id: int - channel ID
        :param message_content: str - message content
        :param timestamp: - datetime object
        :param author_id:
        :return: None
        """
        entry = {
            "user_id": user_id,
            "content": message_content,
            "timestamp": timestamp,
        }

        self.update(
            {"message_id": message_id, "guild_id": guild_id, "channel_id": channel_id, "user_id": author_id},
            {"$push": {"reactions": entry}},
        )

    def remove_reaction_entry(
            self,
            message_id: int,
            guild_id: int,
            user_id: int,
            channel_id: int,
            message_content: str,
            timestamp: datetime.datetime,
            author_id: int) -> None:
        """
        Adds a reaction entry into our interactions DB with the corresponding message.
        :param message_id: int - message ID
        :param guild_id: int - guild ID
        :param user_id: int - user ID
        :param channel_id: int - channel ID
        :param message_content: str - message content
        :param timestamp: - datetime object
        :param author_id:
        :return: None
        """
        entry = {
            "user_id": user_id,
            "content": message_content,
            "timestamp": timestamp,
        }

        self.update(
            {"message_id": message_id, "guild_id": guild_id, "channel_id": channel_id, "user_id": author_id},
            {"$pull": {"reactions": entry}},
        )

    def get_message(self, guild_id: int, message_id: int) -> Optional[Message]:
        """Retrieves a message from the DB cache with the specific guild ID and message ID

        Args:
            guild_id (int): guild to get the message for
            message_id (int): message ID to get the message for

        Returns:
            Optional[Message]: The Message or None
        """
        ret = self.query({"guild_id": guild_id, "message_id": message_id})
        if ret:
            return ret[0]
        return None

    def add_voice_state_entry(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        timestamp: datetime.datetime,
        muted: bool,
        deafened: bool,
        streaming: bool,
    ) -> list:

        doc = {
            "guild_id": guild_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "timestamp": timestamp,
            "muted": muted,
            "muted_time": None if not muted else timestamp,
            "deafened": deafened,
            "deafened_time": None if not deafened else timestamp,
            "streaming": streaming,
            "streaming_time": None if not streaming else timestamp,
            "time_in_vc": 0,
            "time_muted": 0,
            "time_deafened": 0,
            "time_streaming": 0,
            "message_type": ["vc_joined", ],
            "active": True,
            "events": [{"timestamp": timestamp, "event": "joined"}]
        }

        return self.insert(doc)

    def find_active_voice_state(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        timestamp: datetime.datetime
    ) -> Optional[dict]:

        ret = self.query({
            "guild_id": guild_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "active": True
        })
        if ret:
            return ret[0]
        else:
            return None
