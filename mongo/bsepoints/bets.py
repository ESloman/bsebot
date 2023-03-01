
import datetime
from typing import Union, Optional

from bson import ObjectId

from discordbot.bot_enums import TransactionTypes
from mongo import interface
from mongo.bsepoints.points import UserPoints
from mongo.datatypes import Bet
from mongo.db_classes import BestSummerEverPointsDB


class UserBets(BestSummerEverPointsDB):
    """
    Class for interacting with the 'userbets' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self, guilds: list = None):
        """
        Constructor method. We initialise the collection object and also the UserPoints instance we need

        If we are given a list of guilds - then we make sure we have a bet counter object for that guild ID

        :param guilds: list of guild IDs
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "userbets")

        self.user_points = UserPoints()

        if guilds is None:
            guilds = []
        for guild in guilds:
            self.__create_counter_document(guild)

    def __create_counter_document(self, guild_id: int) -> None:
        """
        Method that creates our base 'counter' document for counting bet IDs

        :param guild_id: int - guild ID to create document for
        :return: None
        """
        if not self.query({"type": "counter", "guild_id": guild_id}):
            self.insert({"type": "counter", "guild_id": guild_id, "count": 1})

    def __get_new_bet_id(self, guild_id) -> str:
        """
        Generate new unique ID and return it in the format we want.

        :param guild_id: int - guild ID to create the new unique bet ID for
        :return: str - new unique bet ID
        """
        count = self.query({"type": "counter", "guild_id": guild_id}, projection={"count": True})[0]["count"]
        self.update({"type": "counter", "guild_id": guild_id}, {"$inc": {"count": 1}})
        return f"{count:04d}"

    @staticmethod
    def count_eddies_for_bet(bet: Bet) -> int:
        """Returns the number of eddies on a bet

        Args:
            bet (Bet): the Bet dict

        Returns:
            int: total eddies
        """
        eddies_bet = sum([
            better["points"] for better in bet["betters"].values()
        ])
        return eddies_bet

    def get_all_active_bets(self, guild_id: int) -> list[Bet]:
        """
        Gets all active bets.

        :param guild_id: int - guild ID to get the active bets for
        :return: list of active bets
        """
        bets = self.query({"active": True, "guild_id": guild_id})
        return bets

    def get_all_inactive_pending_bets(self, guild_id: int) -> list[Bet]:
        """
        Gets all the bets that are not active without results

        Args:
            guild_id (int): _description_

        Returns:
            list: _description_
        """
        bets = self.query({"active": False, "result": None, "guild_id": guild_id})
        return bets

    def get_all_pending_bets(self, guild_id: int) -> list[Bet]:
        """
        Gets all 'pending' bets - bets that don't have a result yet.
        Could be active or closed.

        :param guild_id: int - guild ID to get the pending bets for
        :return: list of pending bets
        """
        bets = self.query({"result": None, "guild_id": guild_id})
        return bets

    def get_user_pending_points(self, user_id: int, guild_id: int) -> int:
        """
        Returns a users points from a given guild.

        We search for all the non-closed bets in the DB and get the points directly from there.

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: int - amount of pending points the user has
        """
        pending = 0

        pending_bets = self.query({f"betters.{user_id}": {"$exists": True}, "guild_id": guild_id, "result": None}, )
        for bet in pending_bets:
            our_user = bet["betters"][str(user_id)]
            pending += our_user["points"]

        return pending

    def get_all_pending_bets_for_user(self, user_id: int, guild_id: int) -> list[Bet]:
        """
        Gets all pending bets for a given user_id

        :param user_id: int - The ID of the user to look for
        :param guild_id: int - The guild ID that the user belongs in
        :return: a list of bet dictionaries
        """
        pending_bets = self.query({f"betters.{user_id}": {"$exists": True}, "guild_id": guild_id, "result": None})
        return pending_bets

    def create_new_bet(self,
                       guild_id: int,
                       user_id: int,
                       title: str,
                       options: list,
                       option_dict: dict,
                       timeout: Union[datetime.datetime, None] = None,
                       private: bool = False) -> Bet:
        """
        Creates a new bet and inserts it into the DB.

        :param private:
        :param guild_id: The guild ID to create the bet in
        :param user_id: The user ID that is creating the bet
        :param title: The title of the bet
        :param options: A list of the emoji options
        :param option_dict: A dictionary that has a bit more information about the available options for the bet
        :param timeout: A datetime object for when the bet will be 'closed'
        :return: A bet dictionary
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
            "message_id": None,
            "private": private,
        }
        self.insert(bet_doc)
        return bet_doc

    def get_bet_from_id(self, guild_id: int, bet_id: str) -> Union[Bet, None]:
        """
        Gets an already created bet document from the database.

        :param guild_id: int - The guild ID the bet exists in
        :param bet_id: str - The ID of the bet to get
        :return: a dict of the bet or None if there's no matching bet ID
        """

        ret = self.query({"bet_id": bet_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def add_better_to_bet(
            self,
            bet_id: int,
            guild_id: int,
            user_id: int,
            emoji: str,
            points: int) -> dict:
        """
        Logic for adding a 'better' to a bet.
        If the user is betting on this for the first time - we simply add the details to the DB
        If not, we check that the user has enough points, that they're betting on an option they have
        already bet on and if the bet is still active.

        :param bet_id: int - The ID of the bet to get
        :param guild_id: int - The guild ID the bet exists in
        :param user_id: int - the user ID of the user betting
        :param emoji: : str - the option the user is attempting to bet on
        :param points: int - the amount of points the user is betting
        :return: success dict
        """

        ret = self.query({"bet_id": bet_id, "guild_id": guild_id})[0]
        betters = ret["betters"]

        # checking the user has enough points
        cur_points = self.user_points.get_user_points(user_id, guild_id)
        if (points > cur_points) or cur_points == 0:
            return {"success": False, "reason": "not enough points"}

        # this section is the logic if the user hasn't bet on this bet yet
        if str(user_id) not in betters:
            doc = {
                "user_id": user_id,
                "emoji": emoji,
                "first_bet": datetime.datetime.now(),
                "last_bet": datetime.datetime.now(),
                "points": points,
            }
            self.update({"_id": ret["_id"]}, {"$set": {f"betters.{user_id}": doc}})
            self.user_points.increment_points(
                user_id,
                guild_id,
                points * -1,
                TransactionTypes.BET_PLACE,
                bet_id=bet_id,
                comment="Bet placed through slash command"
            )
            return {"success": True}

        # here we're checking if the user has already bet on the option they have selected
        # if they haven't - then it's an error
        current_better = betters[str(user_id)]
        if emoji != current_better["emoji"]:
            return {"success": False, "reason": "wrong option"}

        self.update(
            {"_id": ret["_id"]},
            {"$inc": {f"betters.{user_id}.points": points}, "$set": {"last_bet": datetime.datetime.now()}}
        )

        self.user_points.increment_points(
            user_id,
            guild_id,
            points * -1,
            TransactionTypes.BET_PLACE,
            bet_id=bet_id,
            comment="Bet placed through slash command"
        )
        new_points = self.user_points.get_user_points(user_id, guild_id)

        if new_points < 0:
            # transaction went wrong somewhere. Reverse all the transactions that we did
            # think this is a case of the user using reactions too quickly
            self.logger.info("Reversing a transaction due to an error")
            self.user_points.increment_points(
                user_id,
                guild_id,
                points,
                TransactionTypes.BET_REFUND,
                bet_id=bet_id,
                comment="Place refund"
            )
            self.update(
                {"_id": ret["_id"]},
                {"$inc": {f"betters.{user_id}.points": -1 * points}, "$set": {"last_bet": datetime.datetime.now()}}
            )
            return {"success": False, "reason": "not enough points"}

        return {"success": True}

    def close_a_bet(self, _id: ObjectId, emoji: Optional[str]) -> None:
        """
        Close a bet from a bet ID.
        Here we also calculate who the winners are and allocate their winnings to them.

        :param _id: ObjectId - the bet to close
        :param emoji: str - the winning result of the bet
        :return: None
        """

        self.update(
            {"_id": _id},
            {"$set": {"active": False, "result": emoji, "closed": datetime.datetime.now()}}
        )
