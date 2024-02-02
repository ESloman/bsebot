"""This is a file for Collection Classes in a MongoDB database.

A MongoDB database can have lots of Collections (basically tables). Each Collection should have a class here
that provides methods for interacting with that Collection.

This particular file contains Collection Classes for the 'bestsummereverpoints' DB.
"""

import datetime

from pymongo.results import UpdateResult

from mongo.baseclass import BaseClass
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes.revolution import RevolutionEventDB


class TicketedEvent(BaseClass):
    """Class for interacting with the 'ticketevents' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__(collection="ticketedevents")


class RevolutionEvent(TicketedEvent):
    """Class for interacting with revolution events."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__()
        self.guilds = Guilds()

    def _create_counter_document(self, guild_id: int) -> None:
        """Method that creates our base 'counter' document for counting loan IDs.

        :param guild_id: int - guild ID to create document for
        :return: None
        """
        if not self.query({"type": "counter", "guild_id": guild_id}, convert=False):
            self.insert({"type": "counter", "guild_id": guild_id, "count": 1})

    def _get_new_id(self, guild_id: int) -> str:
        """Generate new unique ID and return it in the format we want.

        Args:
            guild_id (int): guild ID to create the new unique loan ID for

        Returns:
            str: new unique ID
        """
        self._create_counter_document(guild_id)
        count = self.query({"type": "counter", "guild_id": guild_id}, projection={"count": True}, convert=False)[0][
            "count"
        ]
        self.update({"type": "counter", "guild_id": guild_id}, {"$inc": {"count": 1}})
        return f"{count:03d}"

    @staticmethod
    def make_data_class(event: dict[str, any]) -> RevolutionEventDB:
        """Converts an event dict into a dataclass.

        Args:
            event (dict): the event dict

        Returns:
            RevolutionEventDB: the dataclass
        """
        return RevolutionEventDB(**event)

    def create_event(  # noqa: PLR0913
        self,
        guild_id: int,
        created: datetime.datetime,
        expired: datetime.datetime,
        king_id: int,
        locked_in_eddies: int,
        channel_id: int | None = None,
    ) -> RevolutionEventDB:
        """Create event class. Puts an entry into the DB for future use.

        Args:
            guild_id (int): _description_
            created (datetime.datetime): _description_
            expired (datetime.datetime): _description_
            king_id (int): _description_
            locked_in_eddies (int): _description_
            channel_id (int | None, optional): _description_. Defaults to None.

        Returns:
            RevolutionEventType: _description_
        """
        event_id = self._get_new_id(guild_id)

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
            "times_saved": 0,
        }

        # add guild "pledges" to supporters by default and lock them in
        guild_db = self.guilds.get_guild(guild_id)
        pledges = guild_db.pledged
        event_doc["supporters"].extend(pledges)
        event_doc["users"].extend(pledges)
        event_doc["chance"] += -15 * len(pledges)
        event_doc["locked"] = pledges

        _id = self.insert(document=event_doc)[0]
        event_doc["_id"] = _id
        return self.make_data_class(event_doc)

    def increment_chance(self, event_id: str, guild_id: int, chance: int) -> UpdateResult:
        """Increments the chance the event will pass.

        Args:
            event_id (str): _description_
            guild_id (int): _description_
            chance (int): _description_

        Returns:
            UpdateResult: _description_
        """
        return self.update({"event_id": event_id, "guild_id": guild_id}, {"$inc": {"chance": chance}})

    def get_event(self, guild_id: int, event_id: str) -> RevolutionEventDB | None:
        """Returns the specified event for the given guild.

        Args:
            guild_id (int): _description_
            event_id (str): _description_

        Returns:
            RevolutionEventType: _description_
        """
        ret: list[RevolutionEventDB] = self.query({"guild_id": guild_id, "event_id": event_id})
        if ret:
            return ret[0]
        return None

    def get_open_events(self, guild_id: int) -> list[RevolutionEventDB]:
        """Gets all open events.

        Args:
            guild_id (int): _description_

        Returns:
            list[RevolutionEventType]: _description_
        """
        return self.query({"guild_id": guild_id, "open": True})

    def close_event(self, event_id: str, guild_id: int, success: bool, points: int) -> UpdateResult:
        """Closes an event and sets all the correct flags in the DB.

        Args:
            event_id (str): _description_
            guild_id (int): _description_
            success (bool): _description_
            points (int): _description_

        Returns:
            UpdateResult: _description_
        """
        return self.update(
            {"event_id": event_id, "guild_id": guild_id},
            {"$set": {"success": success, "points_distributed": points, "open": False}},
        )
