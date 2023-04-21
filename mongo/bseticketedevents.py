"""
This is a file for Collection Classes in a MongoDB database.

A MongoDB database can have lots of Collections (basically tables). Each Collection should have a class here
that provides methods for interacting with that Collection.

This particular file contains Collection Classes for the 'bestsummereverpoints' DB.
"""

import datetime

from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes import RevolutionEventType
from mongo.db_classes import BestSummerEverPointsDB


class TicketedEvent(BestSummerEverPointsDB):
    """
    Class for interacting with the 'ticketevents' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method that initialises the vault object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "ticketedevents")


class RevolutionEvent(TicketedEvent):
    """
    Class for interacting with revolution events
    """
    def __init__(self):
        super().__init__()
        self.guilds = Guilds()

    def __create_counter_document(self, guild_id: int) -> None:
        """
        Method that creates our base 'counter' document for counting loan IDs

        :param guild_id: int - guild ID to create document for
        :return: None
        """
        if not self.query({"type": "counter", "guild_id": guild_id}):
            self.insert({"type": "counter", "guild_id": guild_id, "count": 1})

    def __get_new_id(self, guild_id) -> str:
        """
        Generate new unique ID and return it in the format we want.

        :param guild_id: int - guild ID to create the new unique loan ID for
        :return: str - new unique loan ID
        """
        try:
            count = self.query({"type": "counter", "guild_id": guild_id}, projection={"count": True})[0]["count"]
        except IndexError:
            self.__create_counter_document(guild_id)
            count = self.query({"type": "counter", "guild_id": guild_id}, projection={"count": True})[0]["count"]
        self.update({"type": "counter", "guild_id": guild_id}, {"$inc": {"count": 1}})
        return f"{count:03d}"

    def create_event(
            self, guild_id: int,
            created: datetime.datetime,
            expired: datetime.datetime,
            king_id: int,
            locked_in_eddies: int,
            channel_id: int = None,
    ) -> RevolutionEventType:
        """
        Create event class. Puts an entry into the DB for future use.

        :param guild_id:
        :param created:
        :param expired:
        :param king_id:
        :param locked_in_eddies:
        :param channel_id:
        :return:
        """

        event_id = self.__get_new_id(guild_id)

        event_doc = {
            "type": "revolution",
            "event_id": event_id,
            "created": created,
            "expired": expired,
            "chance": 15,
            "revolutionaries": [],
            "supporters": [],
            "neutrals": [],
            "users": [],
            "ticket_buyers": [],
            "open": True,
            "message_id": None,
            "channel_id": channel_id,
            "guild_id": guild_id,
            "king": king_id,
            "points_distributed": 0,
            "eddies_spent": 0,
            "success": None,
            "locked_in_eddies": locked_in_eddies,
            "times_saved": 0
        }

        # add guild "pledges" to supporters by default and lock them in
        guild_db = self.guilds.get_guild(guild_id)
        pledges = guild_db.get("pledged", [])
        event_doc["supporters"].extend(pledges)
        event_doc["users"].extend(pledges)
        event_doc["chance"] += (-15 * len(pledges))
        event_doc["locked"] = pledges

        self.insert(document=event_doc)
        return event_doc

    def increment_eddies_total(self, event_id: str, guild_id: int, points: int):
        """
        Increments the amount of eddies that have been spent on an event

        :param event_id:
        :param guild_id:
        :param points:
        :return:
        """
        return self.update({"event_id": event_id, "guild_id": guild_id}, {"$inc": {"eddies_spent": points}})

    def increment_chance(self, event_id: str, guild_id: int, chance: int):
        """
        Increments the chance the event will pass

        :param event_id:
        :param guild_id:
        :param chance:
        :return:
        """
        return self.update({"event_id": event_id, "guild_id": guild_id}, {"$inc": {"chance": chance}})

    def add_user_to_buyers(self, event_id: str, guild_id: int, user_id: int):
        """
        Adds an individual to the list of ticket buyers

        :param event_id:
        :param guild_id:
        :param user_id:
        :return:
        """
        return self.update({"event_id": event_id, "guild_id": guild_id}, {"$push": {"ticket_buyers": user_id}})

    def get_event(self, guild_id: int, event_id: str) -> RevolutionEventType:
        """
        Returns the specified event for the given guild

        :param guild_id:
        :param event_id:
        :return:
        """
        ret = self.query({"guild_id": guild_id, "event_id": event_id})
        if ret:
            return ret[0]

    def get_open_events(self, guild_id: int) -> list[RevolutionEventType]:
        """
        Gets all open events

        :param guild_id:
        :return:
        """
        ret = self.query({"guild_id": guild_id, "open": True})
        return ret

    def close_event(self, event_id: str, guild_id: int, success: bool, points: int):
        """
        Closes an event and sets all the correct flags in the DB

        :param event_id:
        :param guild_id:
        :param success:
        :param points:
        :return:
        """
        return self.update(
            {"event_id": event_id, "guild_id": guild_id},
            {"$set": {"success": success, "points_distributed": points, "open": False}}
        )
