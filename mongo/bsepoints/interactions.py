"""Interactions collection interface."""

import datetime

from bson import ObjectId

from mongo.baseclass import BaseClass
from mongo.datatypes.message import MessageDB, ReactionDB, ReplyDB, VCInteractionDB


class UserInteractions(BaseClass):
    """Class for interacting with the 'userinteractions' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__(collection="userinteractions")

    @staticmethod
    def make_data_class(message: dict | MessageDB) -> MessageDB | VCInteractionDB:
        """Makes a given message a dataclass.

        Returns:
            MessageDB: _description_
        """
        if isinstance(message, MessageDB):
            return message

        if "vc_joined" in message["message_type"]:
            if "message_id" not in message:
                message["message_id"] = None
            return VCInteractionDB(**message)

        message["reactions"] = [ReactionDB(**react) for react in message.get("reactions", [])]
        message["replies"] = [ReplyDB(**reply) for reply in message.get("replies", [])]
        return MessageDB(**message)

    def query(  # noqa: PLR0913, PLR0917
        self,
        query_dict: dict[str, any],
        limit: int = 1000,
        projection: dict | None = None,
        as_gen: bool = False,
        skip: int | None = None,
        use_paginated: bool = False,
        sort: list[tuple] | None = None,
        convert: bool = True,
    ) -> list[MessageDB]:
        """Overriding to define return type."""
        return super().query(query_dict, limit, projection, as_gen, skip, use_paginated, sort, convert)

    def paginated_query(self, query_dict: dict[str, any], limit: int = 1000, skip: int = 0) -> list[MessageDB]:
        """Overriding to define return type."""
        return [super().paginated_query(query_dict, limit, skip)]

    def get_all_messages_for_server(self, guild_id: int) -> list[MessageDB]:
        """Gets all messages for a given server.

        Args:
            guild_id (int): the server Id to get messages for

        Returns:
            list[MessageDB]: list of messages
        """
        return self.paginated_query({"guild_id": guild_id})

    def get_all_messages_for_channel(self, guild_id: int, channel_id: int) -> list[MessageDB]:
        """Gets all messages for a given channel and guild.

        Args:
            guild_id (int): the server Id to get messages for
            channel_id (int): the channel Id to get messages for

        Returns:
            list[MessageDB]: list of messages
        """
        return self.paginated_query({"guild_id": guild_id, "channel_id": channel_id})

    def add_entry(  # noqa: PLR0913, PLR0917
        self,
        message_id: int,
        guild_id: int,
        user_id: int,
        channel_id: int,
        message_type: list[str],
        message_content: str,
        timestamp: datetime.datetime,
        additional_keys: dict | None = None,
        is_thread: bool = False,
        is_vc: bool = False,
        is_bot: bool = False,
    ) -> MessageDB:
        """Adds an entry into our interactions DB with the corresponding message.

        Args:
            message_id (int): message ID
            guild_id (int): guild ID
            user_id (int): user ID
            channel_id (int): channel ID
            message_type (str): message type
            message_content (str): message content
            timestamp (datetime.datetime): timestamp of the message.
            additional_keys: (dict | None): any additional info. Defaults to None.
            is_thread (bool): whether the entry happened in a thread or not. Defaults to False.
            is_vc (bool): whether the entry happened in a vc or not. Defaults to False.
            is_bot (bool): whether the message came from a bot or not. Defaults to False.
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
            "is_vc": is_vc,
            "is_bot": is_bot,
        }

        if additional_keys:
            message.update(additional_keys)

        result = self.insert(message)
        message["_id"] = result[0]
        return self.make_data_class(message)

    def add_reply_to_message(  # noqa: PLR0913, PLR0917
        self,
        reference_message_id: int,
        message_id: int,
        guild_id: int,
        user_id: int,
        timestamp: datetime.datetime,
        content: str,
        is_bot: bool = False,
    ) -> None:
        """Adds a reply to a message.

        Args:
            reference_message_id (int): _description_
            message_id (int): _description_
            guild_id (int): _description_
            user_id (int): _description_
            timestamp (datetime.datetime): _description_
            content (str): _description_
            is_bot (bool, optional): _description_. Defaults to False.
        """
        entry = {
            "user_id": user_id,
            "content": content,
            "timestamp": timestamp,
            "message_id": message_id,
            "is_bot": is_bot,
        }

        self.update(
            {"message_id": reference_message_id, "guild_id": guild_id},
            {"$push": {"replies": entry}},
        )

    def add_reaction_entry(  # noqa: PLR0913, PLR0917
        self,
        message_id: int,
        guild_id: int,
        user_id: int,
        channel_id: int,
        message_content: str,
        timestamp: datetime.datetime,
        author_id: int,
    ) -> None:
        """Adds a reaction entry into our interactions DB with the corresponding message.

        Args:
            message_id (int): message ID
            guild_id (int): guild ID
            user_id (int): user ID
            channel_id (int): channel ID
            message_content (str): message content
            timestamp (datetime.datetime): when the reaction happened
            author_id (int): the author ID
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

    def remove_reaction_entry(  # noqa: PLR0913, PLR0917
        self,
        message_id: int,
        guild_id: int,
        user_id: int,
        channel_id: int,
        message_content: str,
        timestamp: datetime.datetime,
        author_id: int,
    ) -> None:
        """Adds a reaction entry into our interactions DB with the corresponding message.

        Args:
            message_id (int): message ID
            guild_id (int): guild ID
            user_id (int): user ID
            channel_id (int): channel ID
            message_content (str): message content
            timestamp (datetime.datetime): timestamp
            author_id (int): the author ID
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

    def get_message(self, guild_id: int, message_id: int) -> MessageDB | None:
        """Retrieves a message from the DB cache with the specific guild ID and message ID.

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

    def add_voice_state_entry(  # noqa: PLR0913, PLR0917
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        timestamp: datetime.datetime,
        muted: bool,
        deafened: bool,
        streaming: bool,
    ) -> list[ObjectId]:
        """Adds a voice state entry.

        Args:
            guild_id (int): _description_
            user_id (int): _description_
            channel_id (int): _description_
            timestamp (datetime.datetime): _description_
            muted (bool): _description_
            deafened (bool): _description_
            streaming (bool): _description_

        Returns:
            list: _description_
        """
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
            "message_type": [
                "vc_joined",
            ],
            "active": True,
            "events": [{"timestamp": timestamp, "event": "joined"}],
        }

        return self.insert(doc)

    def find_active_voice_state(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        _: datetime.datetime,
    ) -> VCInteractionDB | None:
        """Finds a voice state activity.

        Args:
            guild_id (int): _description_
            user_id (int): _description_
            channel_id (int): _description_
            _ (datetime.datetime): _description_

        Returns:
            dict | None: _description_
        """
        ret = self.query({"guild_id": guild_id, "user_id": user_id, "channel_id": channel_id, "active": True})
        if ret:
            return ret[0]
        return None
