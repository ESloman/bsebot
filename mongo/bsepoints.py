import datetime
from typing import Union

from mongo import interface
from mongo.db_classes import BestSummerEverPointsDB


class UserPoints(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userpoints' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        super().__init__()
        self._vault = interface.get_collection(self.database, "userpoints")

    def find_user(self, user_id, guild_id):
        """
        Looks up a user in the collection.
        :param user_id:
        :param guild_id:
        :return:
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_user_points(self, user_id, guild_id):
        """
        Returns a users points from a given guild.
        :param user_id:
        :param guild_id:
        :return:
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"points": True})
        return ret[0]["points"]

    def get_user_pending_points(self, user_id, guild_id):
        """
        Returns a users points from a given guild.
        :param user_id:
        :param guild_id:
        :return:
        """
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"pending_points": True})
        return ret[0]["pending_points"]

    def get_all_users_for_guild(self, guild_id):
        """
        Gets all the users from a given guild.
        :param guild_id:
        :return:
        """
        ret = self.query({"guild_id": guild_id}, projection={"points": True, "uid": True})
        return ret

    def set_points(self, user_id, guild_id, points):
        """
        Sets a user's points to a given value.
        :param user_id:
        :param guild_id:
        :param points:
        :return:
        """
        return self.update({"user_id": user_id, "guild_id": guild_id}, {"$set": {"points": points}})

    def set_pending_points(self, user_id, guild_id, points):
        """
        Sets a user's pending points to a given value.
        :param user_id:
        :param guild_id:
        :param points:
        :return:
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$set": {"pending_points": points}})

    def increment_pending_points(self, user_id, guild_id, amount):
        """
        Increases the 'pending' points of specified user
        :param user_id:
        :param guild_id:
        :param amount:
        :return:
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"pending_points": amount}})

    def increment_points(self, user_id, guild_id, amount):
        """
        Increases a users points by a set amount.
        :param user_id:
        :param guild_id:
        :param amount:
        :return:
        """
        return self.update({"uid": user_id, "guild_id": guild_id}, {"$inc": {"points": amount}})

    def decrement_pending_points(self, user_id, guild_id, amount):
        """
        Decreases a users pending points by a set amount.
        :param user_id:
        :param guild_id:
        :param amount:
        :return:
        """
        return self.increment_pending_points(user_id, guild_id, amount * -1)

    def decrement_points(self, user_id, guild_id, amount):
        """
        Decreases a users points by a set amount.
        :param user_id:
        :param guild_id:
        :param amount:
        :return:
        """
        return self.increment_points(user_id, guild_id, amount * -1)

    def create_user(self, user_id, guild_id):
        """
        Create basic user points document.
        :param user_id:
        :param guild_id:
        :return:
        """
        user_doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "points": 10,
            "pending_points": 0
        }
        self.insert(user_doc)


class UserBets(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userbets' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self, guilds=None):
        super().__init__()
        self._vault = interface.get_collection(self.database, "userbets")

        self.user_points = UserPoints()

        if guilds is None:
            guilds = []
        for guild in guilds:
            self.__create_counter_document(guild)

    def __create_counter_document(self, guild_id):
        """
        Method that creates our base 'counter' document for counting bet IDs
        :return:
        """
        if not self.query({"type": "counter", "guild_id": guild_id}):
            self.insert({"type": "counter", "guild_id": guild_id, "count": 1})

    def __get_new_bet_id(self, guild_id):
        """
        Generate new unique ID.
        :return:
        """
        count = self.query({"type": "counter", "guild_id": guild_id}, projection={"count": True})[0]["count"]
        self.update({"type": "counter", "guild_id": guild_id}, {"$inc": {"count": 1}})
        return f"{count:04d}"

    def get_all_active_bets(self, guild_id):
        """
        Gets all active bets.
        :return:
        """
        bets = self.query({"active": True, "guild_id": guild_id})
        return bets

    def create_new_bet(self, guild_id, user_id, title, options, option_dict,
                       timeout: Union[datetime.datetime, None] = None):
        """
        Creates a new bet and inserts it into the DB.
        :param guild_id:
        :param user_id:
        :param title:
        :param options:
        :param option_dict:
        :param timeout:
        :return:
        """
        bet_id = self.__get_new_bet_id(guild_id)
        bet_doc = {
            "bet_id": bet_id,
            "guild_id": guild_id,
            "user": user_id,
            "title": title,
            "options": options,
            "created": datetime.datetime.now(),
            "timeout": timeout,
            "active": True,
            "betters": {},
            "result": None,
            "option_dict": option_dict,
            "channel_id": None,
            "message_id": None
        }
        self.insert(bet_doc)
        return bet_doc

    def get_bet_from_id(self, guild_id, bet_id):
        """
        Gets an already created bet document from the database.
        :param guild_id:
        :param bet_id:
        :return:
        """
        ret = self.query({"bet_id": bet_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def add_better_to_bet(self, bet_id, guild_id, user_id, emoji, points):
        """
        Logic for adding a 'better' to a bet. Makes sure that we have enough points
        and aren't betting on both options.
        :param bet_id:
        :param guild_id:
        :param user_id:
        :param emoji:
        :param points:
        :return:
        """
        ret = self.query({"bet_id": bet_id, "guild_id": guild_id})[0]
        betters = ret["betters"]
        if str(user_id) not in betters:
            doc = {
                "user_id": user_id,
                "emoji": emoji,
                "first_bet": datetime.datetime.now(),
                "last_bet": datetime.datetime.now(),
                "points": points,
            }
            self.update({"_id": ret["_id"]}, {"$set": {f"betters.{user_id}": doc}})
            self.user_points.decrement_points(user_id, guild_id, points)
            return {"success": True}
        current_better = betters[str(user_id)]
        if emoji != current_better["emoji"]:
            return {"success": False, "reason": "wrong option"}

        cur_points = self.user_points.get_user_points(user_id, guild_id)
        if (points > cur_points) or cur_points == 0:
            return {"success": False, "reason": "not enough points"}

        self.update(
            {"_id": ret["_id"]},
            {"$inc": {f"betters.{user_id}.points": points}, "$set": {"last_bet": datetime.datetime.now()}}
        )
        self.user_points.decrement_points(user_id, guild_id, points)
        return {"success": True}

    def close_a_bet(self, bet_id, guild_id, emoji):
        """
        Close a bet from a bet ID
        :param bet_id:
        :param guild_id:
        :param emoji:
        :return:
        """
        ret = self.query({"bet_id": bet_id, "guild_id": guild_id})[0]

        self.update(
            {"_id": ret["_id"]},
            {"$set": {"active": False, "result": emoji, "closed": datetime.datetime.now()}}
        )

        ret_dict = {
            "result": emoji,
            "timestamp": datetime.datetime.now(),
            "losers": {b: ret["betters"][b]["points"]
                       for b in ret["betters"] if ret["betters"][b]["emoji"] != emoji},
            "winners": {}
        }
        for better in [b for b in ret["betters"] if ret["betters"][b]["emoji"] == emoji]:
            points_bet = ret["betters"][better]["points"]
            points_won = points_bet * 2
            ret_dict["winners"][better] = points_won
            self.user_points.increment_points(int(better), guild_id, points_won)

        for better in ret["betters"]:
            points_bet = ret["betters"][better]["points"]
            self.user_points.decrement_pending_points(int(better), guild_id, points_bet)

        return ret_dict


class UserInteractions(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userinteractions' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        super().__init__()
        self._vault = interface.get_collection(self.database, "userinteractions")

    def add_entry(self, message_id, guild_id, user_id, channel_id, message_type, message_content, timestamp):
        """
        Adds an entry into our interactions DB with the corresponding message.
        :param message_id:
        :param guild_id:
        :param user_id:
        :param channel_id:
        :param message_type:
        :param message_content:
        :param timestamp:
        :return:
        """

        message = {
            "message_id": message_id,
            "guild_id": guild_id,
            "user_id": user_id,
            "channel_id": channel_id,
            "message_type": message_type,
            "content": message_content,
            "timestamp": timestamp
        }

        self.insert(message)
