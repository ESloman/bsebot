"""Guilds collection interface."""

import datetime

import pytz
from pymongo.results import InsertOneResult, UpdateResult

from discordbot.bot_enums import ActivityTypes
from mongo.baseclass import BaseClass
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.user import UserDB


class Guilds(BaseClass):  # noqa: PLR0904
    """Class for interacting with the 'guilds' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method for the class. Initialises the collection object."""
        super().__init__(collection="guilds")
        self.user_points: UserPoints = UserPoints()

    @staticmethod
    def make_data_class(data: dict[str, any]) -> GuildDB:
        """Converts the data entry into a dataclass.

        Args:
            data (dict[str, any]): the given entry

        Returns:
            GuildDB: the guild data class
        """
        return GuildDB(**data)

    def get_guild(self, guild_id: int) -> GuildDB | None:
        """Gets an already created guild document from the database.

        :param guild_id: int - The guild ID
        :return: a dict of the guild or None if there's no matching ID
        """
        ret: list[GuildDB] = self.query(
            {"guild_id": guild_id}, projection={"tax_rate_history": False, "king_history": False}
        )
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
        """Inserts a guild into the database.

        Args:
            guild_id (int): _description_
            name (str): _description_
            owner_id (int): _description_
            created (datetime.datetime): _description_

        Returns:
            InsertOneResult: _description_
        """
        doc = {
            "name": name,
            "guild_id": guild_id,
            "owner_id": owner_id,
            "created": created,
            "tax_rate": 0.1,
            "update_messages": False,
            "release_notes": False,
            "wordle": False,
            "valorant_rollcall": False,
            "wordle_reminders": False,
        }

        return self.insert(doc)

    #
    # Channel stuff
    #

    def get_channel(self, guild_id: int) -> int:
        """Gets the bseddies channel to send messages to.

        Args:
            guild_id (int): the guild ID to do this for

        Returns:
            int: the channel ID
        """
        ret: list[GuildDB] = self.query({"guild_id": guild_id}, projection={"channel": True})
        if not ret or not ret[0].channel:
            return None
        return ret[0].channel

    #
    # King stuff
    #

    def get_king(self, guild_id: int, whole_class: bool = False) -> int | UserDB:
        """Gets the King ID for the specified guild.

        Args:
            guild_id (int): the guild ID
            whole_class (bool, optional): Whether to also fetch the user dict. Defaults to False.

        Returns:
            int | dict: king ID, or the user dict
        """
        ret: list[GuildDB] = self.query({"guild_id": guild_id}, projection={"king": True})
        if not ret or not ret[0].king:
            # king ID not set
            return None

        if not whole_class:
            return ret[0].king

        # fetch the user dict
        return self.user_points.find_user(ret[0].king, guild_id)

    def set_king(self, guild_id: int, user_id: int) -> UpdateResult:
        """Sets the king user ID in the guild collection. Updates king history too.

        Args:
            guild_id (int): the guild ID
            user_id (int): the new king user ID

        Returns:
            UpdateResult: return result
        """
        now = datetime.datetime.now(tz=pytz.utc)
        previous_king = self.get_king(guild_id, False)
        previous_doc = {"timestamp": now, "type": ActivityTypes.KING_LOSS, "user_id": previous_king}
        doc = {"timestamp": datetime.datetime.now(tz=pytz.utc), "type": ActivityTypes.KING_GAIN, "user_id": user_id}
        return self.update(
            {"guild_id": guild_id},
            {"$set": {"king": user_id, "king_since": now}, "$push": {"king_history": {"$each": [previous_doc, doc]}}},
        )

    def add_pledger(self, guild_id: int, user_id: int) -> UpdateResult:
        """Add a supporting pledger to the pledges list.

        Args:
            guild_id (int): the guild ID
            user_id (int): the user ID to add

        Returns:
            UpdateResult: return result
        """
        return self.update({"guild_id": guild_id}, {"$push": {"pledged": user_id}})

    def reset_pledges(self, guild_id: int) -> UpdateResult:
        """Reset the pledges.

        Args:
            guild_id (int): the guild ID

        Returns:
            UpdateResult: return result
        """
        return self.update({"guild_id": guild_id}, {"$set": {"pledged": []}})

    def set_revolution_toggle(self, guild_id: int, enabled: bool) -> UpdateResult:
        """Set the bool the enables/disables the revolution event.

        Args:
            guild_id (int): the guild ID
            enabled (bool): whether the revolution event is enabled/disabled

        Returns:
            UpdateResult: return result
        """
        return self.update({"guild_id": guild_id}, {"$set": {"revolution": enabled}})

    #
    # Salary stuff
    #

    def get_daily_minimum(self, guild_id: int) -> int:
        """Gets daily minimum for the given guild.

        Args:
            guild_id (int): guild ID to get min for

        Returns:
            int: the minimum
        """
        ret: list[GuildDB] = self.query({"guild_id": guild_id})
        if ret:
            return ret[0].daily_minimum
        return None

    def set_daily_minimum(self, guild_id: int, amount: int) -> UpdateResult:
        """Updates daily minimum salary for given guild ID with given amount.

        Args:
            guild_id (int): guild ID to update
            amount (int): amount to set daily minimum to

        Returns:
            UpdateResult: update result
        """
        return self.update({"guild_id": guild_id}, {"$set": {"daily_minimum": amount}})

    #
    #  Tax stuff
    #

    def update_tax_history(
        self,
        guild_id: int,
        tax_rate: float,
        supporter_tax_rate: float,
        user_id: int,
    ) -> UpdateResult:
        """Adds entry to tax history."""
        doc = {
            "tax_rate": tax_rate,
            "supporter_tax_rate": supporter_tax_rate,
            "user_id": user_id,
            "timestamp": datetime.datetime.now(tz=pytz.utc),
        }
        return self.update({"guild_id": guild_id}, {"$push": {"tax_rate_history": doc}})

    def set_tax_rate(self, guild_id: int, tax_rate: float, supporter_tax_rate: float) -> UpdateResult:
        """Updates tax rate for given guild ID.

        Args:
            guild_id (int): guild ID to set tax rate for
            tax_rate (float): desired tax rate to set
            supporter_tax_rate (float): desired supporter tax rate to set

        Returns:
            UpdateResult: update result
        """
        return self.update(
            {"guild_id": guild_id},
            {"$set": {"tax_rate": tax_rate, "supporter_tax_rate": supporter_tax_rate}},
        )

    def get_tax_rate(self, guild_id: int) -> tuple[float]:
        """Returns the tax rate for the given guild.

        Args:
            guild_id (int): the guild ID

        Returns:
            float: tax rate as float
        """
        ret: list[GuildDB] = self.query(
            {"guild_id": guild_id}, projection={"tax_rate": True, "supporter_tax_rate": True}
        )
        if not ret or not ret[0].tax_rate:
            self.set_tax_rate(guild_id, 0.1, 0.0)
            self.update_tax_history(guild_id, 0.1, 0.0, 0)
            return 0.1, 0.0
        return ret[0].tax_rate, ret[0].supporter_tax_rate

    #
    # Ad stuff
    #

    def get_last_ad_time(self, guild_id: int) -> datetime.datetime:
        """Gets the last ad time.

        Args:
            guild_id (int): the guild ID to do this for

        Returns:
            dateteime: the time this guild last had a marvel comics ad
        """
        ret: list[GuildDB] = self.query({"guild_id": guild_id}, projection={"last_ad_time": True})
        if not ret or not ret[0].last_ad_time:
            return None
        return ret[0].last_ad_time

    def set_last_ad_time(self, guild_id: int, timestamp: datetime.datetime) -> UpdateResult:
        """Sets the last ad time.

        Args:
            guild_id (int): the guild ID to do this for
            timestamp (datetime): the timestamp to set

        Returns:
            UpdateResult: update result
        """
        return self.update({"guild_id": guild_id}, {"$set": {"last_ad_time": timestamp}})

    #
    # Remind me reminder stuff
    #

    def get_last_remind_me_time(self, guild_id: int) -> datetime.datetime:
        """Gets the last remind me suggestion time.

        Args:
            guild_id (int): the guild ID to do this for

        Returns:
            dateteime: the time this guild last had a marvel comics ad
        """
        ret: list[GuildDB] = self.query({"guild_id": guild_id}, projection={"last_remind_me_suggest_time": True})
        if not ret or not ret[0].last_remind_me_suggest_time:
            return None
        return ret[0].last_remind_me_suggest_time

    def set_last_remind_me_time(self, guild_id: int, timestamp: datetime.datetime) -> UpdateResult:
        """Sets the last remind me suggested time.

        Args:
            guild_id (int): the guild ID to do this for
            timestamp (datetime): the timestamp to set

        Returns:
            UpdateResult: update result
        """
        return self.update({"guild_id": guild_id}, {"$set": {"last_remind_me_suggest_time": timestamp}})

    #
    # Valorant stuff
    #

    def set_valorant_config(
        self, guild_id: int, active: bool, channel: int | None = None, role: int | None = None
    ) -> UpdateResult:
        """Sets valorant config options.

        Args:
            guild_id (int): guild ID to set for
            active (bool): whether valorant roll call is turned on/off for guild
            channel (int, optional): channel ID of channel to post in. Defaults to None.
            role (int, optional): role ID of role to mention

        Returns:
            UpdateResult: update result
        """
        return self.update(
            {"guild_id": guild_id},
            {"$set": {"valorant_rollcall": active, "valorant_channel": channel, "valorant_role": role}},
        )

    #
    # Wordle stuff
    #

    def set_wordle_config(
        self,
        guild_id: int,
        active: bool,
        channel: int | None = None,
        reminders: bool = False,
    ) -> UpdateResult:
        """Sets wordle config options.

        Args:
            guild_id (int): guild ID to set for
            active (bool): whether wordle is turned on/off for guild
            channel (int, optional): channel ID of channel to post in. Defaults to None.
            reminders (bool, optional): whether reminders are on/off for guild. Defaults to False.

        Returns:
            UpdateResult: update result
        """
        return self.update(
            {"guild_id": guild_id},
            {"$set": {"wordle": active, "wordle_channel": channel, "wordle_reminders": reminders}},
        )

    #
    # Revolution stuff
    #

    def set_last_rigged_time(self, guild_id: int) -> UpdateResult:
        """Sets last rigged message time.

        Args:
            guild_id (int): the guild to set this for

        Returns:
            UpdateResult: update result
        """
        now = datetime.datetime.now(tz=pytz.utc)
        return self.update({"guild_id": guild_id}, {"$set": {"last_rigged_time": now}})
