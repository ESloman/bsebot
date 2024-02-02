"""Emojis collection interface."""

import datetime

from bson import ObjectId

from mongo import interface
from mongo.baseclass import BaseClass
from mongo.datatypes.customs import EmojiDB


class ServerEmojis(BaseClass):
    """Class for interacting with the 'serveremojis' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "serveremojis")

    @staticmethod
    def make_data_class(emoji: dict[str, any]) -> EmojiDB:
        """Converts into a dataclass.

        Args:
            emoji (dict): the emoji dict

        Returns:
            EmojiDB: the emoji dataclass
        """
        return EmojiDB(**emoji)

    def get_all_emojis(self, guild_id: int) -> list[EmojiDB]:
        """Gets all emoji objects from the database.

        Args:
            guild_id (int): the guild ID of the server we want emojis for

        Returns:
            list[dict]: a list of emoji dicts
        """
        return self.query({"guild_id": guild_id})

    def get_emoji(self, guild_id: int, emoji_id: int) -> EmojiDB | None:
        """Gets an already created emoji document from the database.

        :param guild_id: int - The guild ID the emoji exists in
        :param emoji_id: str - The ID of the emoji to get
        :return: a dict of the emoji or None if there's no matching bet ID
        """
        ret = self.query({"eid": emoji_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_emoji_from_name(self, guild_id: int, name: str) -> EmojiDB | None:
        """Gets emoji from name.

        Args:
            guild_id (int): _description_
            name (str): _description_

        Returns:
            Emoji | None: _description_
        """
        ret = self.query({"name": name, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def insert_emoji(
        self, emoji_id: int, name: str, created: datetime.datetime, user_id: int, guild_id: int
    ) -> list[ObjectId]:
        """Inserts an emoji into the database.

        Args:
            emoji_id (int): _description_
            name (str): _description_
            created (datetime.datetime): _description_
            user_id (int): _description_
            guild_id (int): _description_

        Returns:
            list: _description_
        """
        doc = {"eid": emoji_id, "name": name, "created": created, "created_by": user_id, "guild_id": guild_id}

        return self.insert(doc)
