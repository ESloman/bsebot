
import datetime
from typing import Union

from mongo import interface
from mongo.datatypes import Emoji
from mongo.db_classes import BestSummerEverPointsDB


class ServerEmojis(BestSummerEverPointsDB):
    """
    Class for interacting with the 'serveremojis' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method for the class. Initialises the collection object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "serveremojis")

    def get_all_emojis(self, guild_id: int) -> list[Emoji]:
        """Gets all emoji objects from the database

        Args:
            guild_id (int): the guild ID of the server we want emojis for

        Returns:
            list[dict]: a list of emoji dicts
        """
        ret = self.query({"guild_id": guild_id})
        return ret

    def get_emoji(self, guild_id: int, emoji_id: int) -> Union[Emoji, None]:
        """
        Gets an already created emoji document from the database.

        :param guild_id: int - The guild ID the emoji exists in
        :param emoji_id: str - The ID of the emoji to get
        :return: a dict of the emoji or None if there's no matching bet ID
        """

        ret = self.query({"eid": emoji_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_emoji_from_name(self, guild_id: int, name: str) -> Union[Emoji, None]:
        """

        :param guild_id:
        :param name:
        :return:
        """
        ret = self.query({"name": name, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def insert_emoji(
            self,
            emoji_id: int,
            name: str,
            created: datetime.datetime,
            user_id: int,
            guild_id: int
    ) -> list:
        doc = {
            "eid": emoji_id,
            "name": name,
            "created": created,
            "created_by": user_id,
            "guild_id": guild_id
        }

        return self.insert(doc)
