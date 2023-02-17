import datetime
from typing import Union, Optional

from pymongo.results import InsertOneResult, UpdateResult

from discordbot.bot_enums import ActivityTypes
from mongo import interface
from mongo.datatypes import GuildDB
from mongo.db_classes import BestSummerEverPointsDB
from mongo.bsepoints.points import UserPoints


class Guilds(BestSummerEverPointsDB):
    """
    Class for interacting with the 'guilds' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method for the class. Initialises the collection object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "guilds")
        self.user_points = UserPoints()

    def get_guild(self, guild_id: int) -> Union[GuildDB, None]:
        """
        Gets an already created guild document from the database.

        :param guild_id: int - The guild ID
        :return: a dict of the guild or None if there's no matching ID
        """

        ret = self.query({"guild_id": guild_id}, projection={"tax_rate_history": False, "king_history": False})
        if ret:
            return ret[0]
        return None

    def insert_guild(
            self,
            guild_id: int,
            name: str,
            owner_id: int,
            created: datetime.datetime,
    ) -> InsertOneResult:
        doc = {
            "name": name,
            "guild_id": guild_id,
            "owner_id": owner_id,
            "created": created,
            "tax_rate": 0.1,
            "update_messages": False
        }

        return self.insert(doc)

    #
    # Channel stuff
    #

    def get_channel(self, guild_id: int) -> int:
        """
        Gets the bseddies channel to send messages to

        Args:
            guild_id (int): the guild ID to do this for

        Returns:
            int: the channel ID
        """
        ret = self.query({"guild_id": guild_id}, {"channel": True})
        if not ret or "channel" not in ret[0]:
            return None
        ret = ret[0]
        return ret["channel"]

    #
    # King stuff
    #

    def get_king(self, guild_id: int, whole_class: bool = False) -> int | dict:
        """Gets the King ID for the specified guild

        Args:
            guild_id (int): the guild ID
            whole_class (bool, optional): Whether to also fetch the user dict. Defaults to False.

        Returns:
            int | dict: king ID, or the user dict
        """
        ret = self.query({"guild_id": guild_id}, projection={"king": True})
        if not ret or "king" not in ret[0]:
            # king ID not set
            return None

        ret = ret[0]
        if not whole_class:
            return ret["king"]

        # fetch the user dict
        return self.user_points.find_user(ret["king"], guild_id)

    def set_king(self, guild_id: int, user_id: int) -> UpdateResult:
        """Sets the king user ID in the guild collection. Updates king history too.

        Args:
            guild_id (int): the guild ID
            user_id (int): the new king user ID

        Returns:
            UpdateResult: return result
        """
        now = datetime.datetime.now()
        previous_king = self.get_king(guild_id, False)
        previous_doc = {"timestamp": now, "type": ActivityTypes.KING_LOSS, "user_id": previous_king}
        doc = {"timestamp": datetime.datetime.now(), "type": ActivityTypes.KING_GAIN, "user_id": user_id}
        ret = self.update(
            {"guild_id": guild_id},
            {"$set": {"king": user_id, "king_since": now}, "$push": {"king_history": {"$each": [previous_doc, doc]}}}
        )
        return ret

    def get_king_time(self, guild_id: int) -> datetime.datetime:
        """
        Returns the time that the current King has been King

        Args:
            guild_id (int): the guild ID

        Returns:
            datetime.datetime: the datetime object
        """
        ret = self.query({"guild_id": guild_id}, projection={"king_since": True})
        if not ret or "king" not in ret[0]:
            # king_since not set
            return None
        ret = ret[0]
        return ret["king"]

    def add_pledger(self, guild_id: int, user_id: int) -> UpdateResult:
        """
        Add a supporting pledger to the pledges list

        Args:
            guild_id (int): the guild ID
            user_id (int): the user ID to add

        Returns:
            UpdateResult: return result
        """

        return self.update({"guild_id": guild_id}, {"$push": {"pledged": user_id}})

    def reset_pledges(self, guild_id: int) -> UpdateResult:
        """
        Reset the pledges

        Args:
            guild_id (int): the guild ID

        Returns:
            UpdateResult: return result
        """

        return self.update({"guild_id": guild_id}, {"$set": {"pledged": []}})

    #
    # Hash stuff
    #

    def get_update_message(self, guild_id: int) -> bool:
        """
        Gets whether or not we should send bot update messages to this guild. Default is false.
        """
        ret = self.query({"guild_id": guild_id}, projection={"update_messages": True})
        if not ret or "update_messages" not in ret[0]:
            return False
        return ret["update_messages"]

    def get_last_hash(self, guild_id: int) -> Optional[str]:
        """
        Get last update hash for the specific guild

        Args:
            guild_id (int): guild ID to get hash for

        Returns:
            Optional[str]: The hash or None
        """
        ret = self.query({"guild_id": guild_id}, projection={"hash": True})
        if not ret or "hash" not in ret[0]:
            return None
        ret = ret[0]
        return ret["hash"]

    def set_last_hash(self, guild_id: int, hash: str) -> UpdateResult:
        """
        Sets hash of last update message

        Args:
            guild_id (int): guild ID to set hash for
            hash (str): the hash value

        Returns:
            UpdateResult: _description_
        """
        return self.update({"guild_id": guild_id}, {"$set": {"hash": hash}})

    def get_update_channel(self, guild_id: int) -> Optional[int]:
        """
        Gets channel we should send update messages to

        Args:
            guild_id (int): the guild ID

        Returns:
            int: the channel ID
        """
        return self.get_channel(guild_id)

    #
    #  Release stuff
    #

    def get_release_flag(self, guild_id: int) -> bool:
        """_summary_

        Args:
            guild_id (int): _description_

        Returns:
            bool: _description_
        """
        ret = self.query({"guild_id": guild_id}, projection={"release_notes": True})
        if not ret or "release_notes" not in ret[0]:
            self.update({"guild_id": guild_id}, {"$set": {"release_notes": False}})
            return False
        ret = ret[0]
        return ret["release_notes"]

    def get_latest_release(self, guild_id: int) -> Optional[str]:
        """_summary_

        Args:
            guild_id (int): _description_

        Returns:
            bool: _description_
        """
        ret = self.query({"guild_id": guild_id}, projection={"release_ver": True})
        if not ret or "release_ver" not in ret[0]:
            return None
        ret = ret[0]
        return ret["release_ver"]

    def set_latest_release(self, guild_id: int, release_ver: str) -> UpdateResult:
        """_summary_

        Args:
            guild_id (int): _description_
            release_ver (str): _description_

        Returns:
            UpdateResult: _description_
        """
        return self.update({"guild_id": guild_id}, {"$set": {"release_ver": release_ver}})

    #
    #  Tax stuff
    #

    def update_tax_history(
        self,
        guild_id: int,
        tax_rate: float,
        supporter_tax_rate: float,
        user_id: int
    ) -> UpdateResult:
        """
        Adds entry to tax history
        """
        doc = {
            "tax_rate": tax_rate,
            "supporter_tax_rate": supporter_tax_rate,
            "user_id": user_id, "timestamp": datetime.datetime.now()
        }
        return self.update({"guild_id": guild_id}, {"$push": {"tax_rate_history": doc}})

    def set_tax_rate(
        self,
        guild_id: int,
        tax_rate: float,
        supporter_tax_rate: float
    ) -> UpdateResult:
        """
        Updates tax rate for given guild ID

        Args:
            guild_id (int): guild ID to set tax rate for
            tax_rate (float): desired tax rate to set
            supporter_tax_rate (float): desired supporter tax rate to set

        Returns:
            UpdateResult: update result
        """
        return self.update(
            {"guild_id": guild_id},
            {"$set": {"tax_rate": tax_rate, "supporter_tax_rate": supporter_tax_rate}}
        )

    def get_tax_rate(
        self,
        guild_id: int
    ) -> tuple[float]:
        """
        Returns the tax rate for the given guild

        Args:
            guild_id (int): the guild ID

        Returns:
            float: tax rate as float
        """
        ret = self.query({"guild_id": guild_id}, projection={"tax_rate": True, "supporter_tax_rate": True})
        if not ret or "tax_rate" not in ret[0]:
            self.set_tax_rate(guild_id, 0.1, 0.0)
            self.update_tax_history(guild_id, 0.1, 0.0, 0)
            return 0.1, 0.0
        ret = ret[0]
        return ret["tax_rate"], ret["supporter_tax_rate"]
