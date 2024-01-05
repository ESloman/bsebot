"""Points collection interface."""

import datetime

from pymongo.results import UpdateResult

from discordbot.bot_enums import TransactionTypes
from mongo import interface
from mongo.bsepoints.transactions import UserTransactions
from mongo.datatypes import User
from mongo.db_classes import BestSummerEverPointsDB


class UserPoints(BestSummerEverPointsDB):
    """Class for interacting with the 'userpoints' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "userpoints")
        self._trans = UserTransactions()

    def __check_highest_eddie_count(self, user_id: int, guild_id: int) -> None:
        """Internal function for making sure the user always has the high score set correctly.

        :param user_id:
        :param guild_id:
        :return:
        """
        ret = self.query(
            {"uid": user_id, "guild_id": guild_id},
            projection={"_id": True, "high_score": True, "points": True},
        )[0]
        if ret["points"] > ret.get("high_score", 0):
            self.update({"_id": ret["_id"]}, {"$set": {"high_score": ret["points"]}})

    def find_user_guildless(self, user_id: int) -> list[User]:
        """Returns all matching user objects for the given ID.

        Args:
            user_id (int): the user ID to search for

        Returns:
            list[User]: the user objects for each guild the user belongs to
        """
        ret = self.query({"uid": user_id})
        return [User(**_user) for _user in ret]

    def find_user(self, user_id: int, guild_id: int, projection: dict | None = None) -> User | None:
        """Looks up a user in the collection.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param projection:
        :return: either a user dict or None if the user couldn't be found
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection=projection)
        if ret:
            return User(**ret[0])
        return None

    def get_user_points(self, user_id: int, guild_id: int) -> int:
        """Returns a users points from a given guild.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - number of points the user has
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"points": True})
        return ret[0]["points"]

    def get_user_daily_minimum(self, user_id: int, guild_id: int) -> int:
        """Returns the user's daily minimum points.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - user's 'daily minimum'
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"daily_minimum": True})
        return ret[0]["daily_minimum"]

    def get_all_users_for_guild(self, guild_id: int, projection: dict | None = None) -> list[User]:
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

        ret = self.query({"guild_id": guild_id}, projection=projection)
        return [User(**_user) for _user in ret]

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
            self.__check_highest_eddie_count(user_id, guild_id)
        # add transaction here
        self._trans.add_transaction(user_id, guild_id, transaction_type, amount, **kwargs)
        return ret

    def increment_daily_minimum(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """Increments the user's daily minimum points by a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to increase daily minimum by
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"daily_minimum": amount}})

    def decrement_daily_minimum(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """Decreases a user's daily minimum points by set amount.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to decrease daily minimum
        :return: UpdateResults object
        """
        return self.increment_daily_minimum(user_id, guild_id, amount * -1)

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

        This toggle quickly tells us who's get in the DB
        :param user_id:
        :param guild_id:
        :param value:
        :return:
        """
        self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"king": value}})

    def get_current_king(self, guild_id: int) -> User | None:
        """Gets current King.

        Args:
            guild_id (int): _description_

        Returns:
            User: _description_
        """
        ret = self.query({"guild_id": guild_id, "king": True})
        if ret:
            return User(**ret[0])
        return None

    @staticmethod
    def get_king_info(king_user: dict[str, any]) -> dict:
        """Function for calculating king stats from a given user dictionary.

        :param king_user:
        :return:
        """
        act_history = king_user.get("activity_history", [])
        kingstuff = [a for a in act_history if a["type"] in {1, 2}]
        gain = None
        total_time = 0
        times_king = 0
        all_times = []
        current_run = 0
        for k in kingstuff:
            if k["type"] == 1:
                gain = k["timestamp"]
                times_king += 1
                if kingstuff.index(k) != (len(kingstuff) - 1):
                    continue
                now = datetime.datetime.now()
                t = (now - gain).total_seconds()
                all_times.append(t)
                total_time += t
                current_run = t
                continue

            if gain is not None:
                t = (k["timestamp"] - gain).total_seconds()
                all_times.append(t)
                total_time += t
                gain = None

        return {"times": times_king, "all_times": all_times, "total": total_time, "current": current_run}
