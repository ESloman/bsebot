"""Channels collection interface."""

import dataclasses
import datetime

from mongo.baseclass import BaseClass
from mongo.datatypes.channel import ChannelDB


class GuildChannels(BaseClass):
    """Class for interacting with the 'channels' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__(collection="channels")

    @staticmethod
    def make_data_class(data: dict[str, any]) -> ChannelDB:
        """Convert the dict into a dataclass.

        Args:
            data (dict): the activity dict

        Returns:
            ChannelDB: the dataclass.
        """
        return ChannelDB(**data)

    def find_channel(self, guild_id: int, channel_id: int) -> ChannelDB | None:
        """Finds a channel from the database.

        Args:
            guild_id (int): _description_
            channel_id (int): _description_

        Returns:
            ChannelDB | None: _description_
        """
        channel = self.query({"guild_id": guild_id, "channel_id": channel_id})
        return channel[0] if channel else None

    def insert_channel(  # noqa: PLR0913, PLR0917
        self,
        guild_id: int,
        channel_id: int,
        channel_type: int,
        name: str,
        created: datetime.datetime,
        category_id: int,
        is_nsfw: bool = False,
    ) -> ChannelDB:
        """Inserts a channel into the database.

        Args:
            guild_id (int): the guild ID.
            channel_id (int): the channel ID.
            channel_type (int): the type of channel.
            name (str): the channel name.
            created (datetime.datetime): when the channel was created.
            category_id (int): the category ID of the channel.
            is_nsfw (bool, optional): whether the channel is NSFW or not. Defaults to False.

        Returns:
            ChannelDB: the database object
        """
        doc = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "type": channel_type,
            "name": name,
            "created": created,
            "category_id": category_id,
            "is_nsfw": is_nsfw,
        }

        _id = self.insert(doc)[0]
        doc["_id"] = _id
        return self.make_data_class(doc)

    def update_channel(self, channel_db: ChannelDB, name: str, is_nsfw: bool = False) -> ChannelDB:
        """Updates a channel in the database.

        Only update fields we care about that change.

        Args:
            channel_db (ChannelDB): the original channel database object.
            name (str): the channel name.
            is_nsfw (bool, optional): whether the channel is NSFW or not. Defaults to False.

        Returns:
            ChannelDB: the new channel database object
        """
        self.update({"_id": channel_db._id}, {"$set": {"name": name, "is_nsfw": is_nsfw}})  # noqa: SLF001
        channel_db: ChannelDB = dataclasses.replace(channel_db, name=name, is_nsfw=is_nsfw)
        return channel_db
