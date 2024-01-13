"""Points collection interface."""

import typing

from pymongo.results import UpdateResult

from discordbot.bot_enums import TransactionTypes
from mongo.baseclass import BaseClass
from mongo.bsepoints.transactions import UserTransactions
from mongo.datatypes.user import UserDB


class UserPoints(BaseClass):
    """Class for interacting with the 'userpoints' MongoDB collection in the 'bestsummereverpoints' DB."""

    _MINIMUM_PROJECTION_DICT: typing.ClassVar = {
        "_id": True,
        "guild_id": True,
        "name": True,
        "uid": True,
        "points": True,
        "king": True,
    }

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__(collection="userpoints")
        self._trans = UserTransactions()

    def _check_highest_eddie_count(self, user_id: int, guild_id: int) -> None:
        """Internal function for making sure the user always has the high score set correctly.

        :param user_id:
        :param guild_id:
        :return:
        """
        try:
            ret: UserDB = self.query(
                {"uid": user_id, "guild_id": guild_id},
                projection={"_id": True, "high_score": True, "points": True},
            )[0]
        except IndexError:
            return

        if ret.points > ret.high_score:
            self.update({"_id": ret._id}, {"$set": {"high_score": ret.points}})  # noqa: SLF001

    @staticmethod
    def make_data_class(user: dict[str, any]) -> UserDB:
        """Converts a user dict into a dataclass.

        Args:
            user (dict): the user to convert

        Returns:
            UserDB: the dataclass
        """
        return UserDB(**user)

    def find_user_guildless(self, user_id: int) -> list[UserDB]:
        """Returns all matching user objects for the given ID.

        Args:
            user_id (int): the user ID to search for

        Returns:
            list[User]: the user objects for each guild the user belongs to
        """
        return self.query({"uid": user_id})

    def find_user(self, user_id: int, guild_id: int, projection: dict | None = None) -> UserDB | None:
        """Looks up a user in the collection.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param projection:
        :return: either a user dict or None if the user couldn't be found
        """
        if projection is not None:
            self._update_projection(projection)

        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection=projection)
        if ret:
            return ret[0]
        return None

    def get_user_points(self, user_id: int, guild_id: int) -> int:
        """Returns a users points from a given guild.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - number of points the user has
        """
        ret: list[UserDB] = self.query({"uid": user_id, "guild_id": guild_id}, projection={"points": True})
        return ret[0].points

    def get_user_daily_minimum(self, user_id: int, guild_id: int) -> int:
        """Returns the user's daily minimum points.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - user's 'daily minimum'
        """
        ret: list[UserDB] = self.query({"uid": user_id, "guild_id": guild_id}, projection={"daily_minimum": True})
        return ret[0].daily_minimum

    def get_all_users_for_guild(self, guild_id: int, projection: dict | None = None) -> list[UserDB]:
        """Gets all the users from a given guild.

        :param guild_id: int - The guild ID to get users for
        :return: list of user dictionaries
        """
        if projection is None:
            projection = {
                "points": True,
                "uid": True,
                "guild_id": True,
                "name": True,
                "king": True,
                "daily_minimum": True,
                "high_score": True,
                "inactive": True,
                "supporter_type": True,
            }

        self._update_projection(projection)

        return self.query({"guild_id": guild_id}, projection=projection)

    def set_daily_minimum(self, user_id: int, guild_id: int, points: int) -> UpdateResult:
        """Sets the user's daily minimum points to a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param points: int - points to set the user's daily minimum to
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"daily_minimum": points}})

    def increment_points(
        self,
        user_id: int,
        guild_id: int,
        amount: int,
        transaction_type: TransactionTypes,
        **kwargs: dict[str, any],
    ) -> UpdateResult:
        """Increases a user's points by a set amount.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to increase pending points by
        :return: UpdateResults object
        """
        ret = self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"points": amount}})
        if amount > 0:
            self._check_highest_eddie_count(user_id, guild_id)
        self._trans.add_transaction(user_id, guild_id, transaction_type, amount, **kwargs)
        return ret

    def create_user(self, user_id: int, guild_id: int, name: str, dailies: bool = False) -> None:
        """Create basic user points document.

        :param dailies:
        :param user_id: int - The ID of the user to look for
        :param name: str - username
        :param guild_id: int - The guild ID that the user belongs in
        :return: None
        """
        user_doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "name": name,
            "points": 10,
            "pending_points": 0,
            "inactive": False,
            "daily_minimum": 5,
            "transaction_history": [],
            "daily_eddies": dailies,
            "king": False,
            "high_score": 10,
        }
        self.insert(user_doc)
        self._trans.add_transaction(user_id, guild_id, TransactionTypes.USER_CREATE, 10, comment="User created")

    def set_daily_eddies_toggle(self, user_id: int, guild_id: int, value: bool, summary_enabled: bool = False) -> None:
        """Sets the "daily eddies" toggle for the given user.

        This toggle determines if the user will receive the daily allowance messages from the bot.
        :param user_id: the user id to use
        :param guild_id: the guild id
        :param value: bool - whether or not the messages should be sent
        :param summary_enabled: bool - whether the daily summary should be sent to this user
        :return:
        """
        if guild_id:
            self.update(
                {"uid": user_id, "guild_id": guild_id},
                {"$set": {"daily_eddies": value, "daily_summary": summary_enabled}},
            )
        else:
            self.update(
                {"uid": user_id},
                {"$set": {"daily_eddies": value, "daily_summary": summary_enabled}},
                many=True,
            )

    def set_king_flag(self, user_id: int, guild_id: int, value: bool) -> None:
        """Sets the 'daily king' toggle for the given user.

        Args:
            user_id (int): the ID of the user to set
            guild_id (int): the ID of the guild to set
            value (bool): whether the user is King or not
        """
        self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"king": value}})

    def get_current_king(self, guild_id: int) -> UserDB | None:
        """Gets current King.

        Args:
            guild_id (int): the guild ID to find the KING for.

        Returns:
            UserDB | None: the user or None.
        """
        ret: list[UserDB] = self.query({"guild_id": guild_id, "king": True})
        if ret:
            return ret[0]
        return None
