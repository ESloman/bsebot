"""Stickers collection interface."""

import datetime

from bson import ObjectId

from mongo.baseclass import BaseClass
from mongo.datatypes.customs import StickerDB


class ServerStickers(BaseClass):
    """Class for interacting with the 'serverstickers' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__(collection="serverstickers")

    @staticmethod
    def make_data_class(sticker: dict[str, any]) -> StickerDB:
        """Converts into a dataclass.

        Args:
            sticker (dict): the sticker dict

        Returns:
            StickerDB: the emoji dataclass
        """
        return StickerDB(**sticker)

    def get_sticker(self, guild_id: int, sticker_id: int) -> StickerDB | None:
        """Gets an already created sticker document from the database.

        :param guild_id: int - The guild ID the sticker exists in
        :param sticker_id: str - The ID of the sticker to get
        :return: a dict of the sticker or None if there's no matching bet ID
        """
        ret: list[StickerDB] = self.query({"stid": sticker_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_sticker_from_name(self, guild_id: int, name: str) -> StickerDB | None:
        """Get sticker from name.

        Args:
            guild_id (int): _description_
            name (str): _description_

        Returns:
            Sticker | None: _description_
        """
        ret: list[StickerDB] = self.query({"name": name, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def insert_sticker(
        self, emoji_id: int, name: str, created: datetime.datetime, user_id: int, guild_id: int
    ) -> list[ObjectId]:
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
