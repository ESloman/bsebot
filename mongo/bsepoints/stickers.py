"""Stickers collection interface."""

import datetime

from mongo import interface
from mongo.datatypes import Sticker
from mongo.db_classes import BestSummerEverPointsDB


class ServerStickers(BestSummerEverPointsDB):
    """Class for interacting with the 'serverstickers' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "serverstickers")

    def get_sticker(self, guild_id: int, sticker_id: int) -> Sticker | None:
        """Gets an already created sticker document from the database.

        :param guild_id: int - The guild ID the sticker exists in
        :param sticker_id: str - The ID of the sticker to get
        :return: a dict of the sticker or None if there's no matching bet ID
        """
        ret = self.query({"stid": sticker_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_sticker_from_name(self, guild_id: int, name: str) -> Sticker | None:
        """Get sticker from name.

        Args:
            guild_id (int): _description_
            name (str): _description_

        Returns:
            Sticker | None: _description_
        """
        ret = self.query({"name": name, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def insert_sticker(self, emoji_id: int, name: str, created: datetime.datetime, user_id: int, guild_id: int) -> list:
        """Inserts a sticker.

        Args:
            emoji_id (int): _description_
            name (str): _description_
            created (datetime.datetime): _description_
            user_id (int): _description_
            guild_id (int): _description_

        Returns:
            list: _description_
        """
        doc = {"stid": emoji_id, "name": name, "created": created, "created_by": user_id, "guild_id": guild_id}

        return self.insert(doc)
