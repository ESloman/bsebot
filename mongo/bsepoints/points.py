import datetime
from typing import Union, Optional

from pymongo.results import UpdateResult

from mongo import interface
from mongo.datatypes import User
from mongo.db_classes import BestSummerEverPointsDB


class UserPoints(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userpoints' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method that initialises the vault object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "userpoints")

    def __check_highest_eddie_count(self, user_id: int, guild_id: int):
        """
        Internal function for making sure the user always has the high score set correctly
        :param user_id:
        :param guild_id:
        :return:
        """
        ret = self.query(
            {"uid": user_id, "guild_id": guild_id}, projection={"_id": True, "high_score": True, "points": True}
        )[0]
        if ret["points"] > ret.get("high_score", 0):
            self.update({"_id": ret["_id"]}, {"$set": {"high_score": ret["points"]}})

    def find_user(self, user_id: int, guild_id: int, projection=None) -> Union[User, None]:
        """
        Looks up a user in the collection.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param projection:
        :return: either a user dict or None if the user couldn't be found
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection=projection)
        if ret:
            return ret[0]
        return None

    def get_user_points(self, user_id: int, guild_id: int) -> int:
        """
        Returns a users points from a given guild.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - number of points the user has
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"points": True})
        return ret[0]["points"]

    def get_user_daily_minimum(self, user_id: int, guild_id: int) -> int:
        """
        Returns the user's daily minimum points.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - user's 'daily minimum'
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"daily_minimum": True})
        return ret[0]["daily_minimum"]

    def get_all_users_for_guild(self, guild_id: int, projection: Optional[dict] = None) -> list[User]:
        """
        Gets all the users from a given guild.

        :param guild_id: int - The guild ID to get users for
        :return: list of user dictionaries
        """

        if projection is None:
            projection = {
                "points": True,
                "uid": True,
                "daily_minimum": True,
                "high_score": True,
                "inactive": True,
                "supporter_type": True
            }

        ret = self.query(
            {"guild_id": guild_id},
            projection=projection
        )
        return ret

    def set_points(self, user_id: int, guild_id: int, points: int) -> UpdateResult:
        """
        Sets a user's points to a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param points: int - points to set the user to
        :return: UpdateResults object
        """
        ret = self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"points": points}})
        self.__check_highest_eddie_count(user_id, guild_id)
        return ret

    def set_pending_points(self, user_id: int, guild_id: int, points: int) -> UpdateResult:
        """
        Sets a user's pending points to a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param points: int - points to set the user's pending value to
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"pending_points": points}})

    def set_daily_minimum(self, user_id, guild_id, points) -> UpdateResult:
        """
        Sets the user's daily minimum points to a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param points: int - points to set the user's daily minimum to
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"daily_minimum": points}})

    def increment_pending_points(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Increases the 'pending' points of specified user

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to increase pending points by
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"pending_points": amount}})

    def increment_points(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Increases a user's points by a set amount.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to increase pending points by
        :return: UpdateResults object
        """
        ret = self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"points": amount}})
        if amount > 0:
            self.__check_highest_eddie_count(user_id, guild_id)
        return ret

    def increment_daily_minimum(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Increments the user's daily minimum points by a given value.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to increase daily minimum by
        :return: UpdateResults object
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"daily_minimum": amount}})

    def decrement_pending_points(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Decreases a user's pending points by a set amount.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to decrease pending points by
        :return: UpdateResults object
        """
        return self.increment_pending_points(user_id, guild_id, amount * -1)

    def decrement_points(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Decreases a user's points by a set amount.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to decrease points by
        :return: UpdateResults object
        """
        return self.increment_points(user_id, guild_id, amount * -1)

    def decrement_daily_minimum(self, user_id: int, guild_id: int, amount: int) -> UpdateResult:
        """
        Decreases a user's daily minimum points by set amount

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param amount: int - amount to decrease daily minimum
        :return: UpdateResults object
        """
        return self.increment_daily_minimum(user_id, guild_id, amount * -1)

    def create_user(self, user_id: int, guild_id: int, dailies: bool = False) -> None:
        """
        Create basic user points document.

        :param dailies:
        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: None
        """
        user_doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "points": 10,
            "pending_points": 0,
            "inactive": False,
            "daily_minimum": 5,
            "transaction_history": [],
            "daily_eddies": dailies,
            "king": False,
            "high_score": 10
        }
        self.insert(user_doc)

    def set_daily_eddies_toggle(self, user_id: int, guild_id: int, value: bool) -> None:
        """
        Sets the "daily eddies" toggle for the given user.
        This toggle determines if the user will receive the daily allowance messages from the bot.
        :param user_id: the user id to use
        :param guild_id: the guild id
        :param value: bool - whether or not the messages should be sent
        :return:
        """
        self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"daily_eddies": value}})

    def set_king_flag(self, user_id: int, guild_id: int, value: bool) -> None:
        """
        Sets the 'daily king' toggle for the given user.
        This toggle quickly tells us who's get in the DB
        :param user_id:
        :param guild_id:
        :param value:
        :return:
        """
        self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"king": value}})

    def get_current_king(self, guild_id: int) -> User:
        """

        :param guild_id:
        :return:
        """
        ret = self.query({"guild_id": guild_id, "king": True})
        if ret:
            return ret[0]

    def append_to_transaction_history(self, user_id: int, guild_id: int, activity: dict) -> UpdateResult:
        """
        Add an item to a user's transaction history

        Activity must be in the format:
        {
            'type': TRANSACTION_TYPE
            'amount': AMOUNT OF EDDIES GAINED/LOST (this should be positive for gain / negative for loss)
            'bet_id': OPTIONAL. Bet ID of bet user gained/lost eddies on
            'user_id': OPTIONAL. User ID user gave/received eddies to/from
            'timestamp': DATETIME OBJECT FOR TIMESTAMP
            'comment': OPTIONAL. Comment as to what happened
        }

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :param activity: the activity dict to add to the transaction history
        :return: None
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$push": {"transaction_history": activity}})

    def append_to_activity_history(self, user_id: int, guild_id: int, activity: dict) -> None:
        """
        Add an item to a user's activity history

        Activity must be in the format:
        {
            'type': ACTIVITY_TYPE,
            'timestamp': DATETIME OBJECT FOR TIMESTAMP
            'comment': OPTIONAL. Comment as to what happened
        }

        :param user_id:
        :param guild_id:
        :param activity:
        :return:
        """
        self.update({"uid": user_id, "guild_id": guild_id}, {"$push": {"activity_history": activity}})

    @staticmethod
    def get_king_info(king_user: dict) -> dict:
        """
        Function for calculating king stats from a given user dictionary
        :param king_user:
        :return:
        """
        act_history = king_user.get("activity_history", [])
        kingstuff = [a for a in act_history if a["type"] in [1, 2]]
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
                else:
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