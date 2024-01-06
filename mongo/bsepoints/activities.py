"""Activities collection interface."""

import dataclasses
import datetime

from pymongo.results import InsertManyResult, InsertOneResult

from discordbot.bot_enums import ActivityTypes
from mongo import interface
from mongo.datatypes.actions import ActivityDB
from mongo.db_classes import BestSummerEverPointsDB


class UserActivities(BestSummerEverPointsDB):
    """Class for interacting with the 'useractivities' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "useractivities")

    @staticmethod
    def make_data_class(activity: dict) -> ActivityDB:
        """Convert the dict into a dataclass.

        Args:
            activity (dict): the activity dict

        Returns:
            ActivityDB: the dataclass.
        """
        cls_fields = {f.name for f in dataclasses.fields(ActivityDB)}
        extras = {k: v for k, v in activity.items() if k not in cls_fields}
        return ActivityDB(**{k: v for k, v in activity.items() if k in cls_fields}, extras=extras)

    def add_activity(
        self,
        user_id: int,
        guild_id: int,
        activity_type: ActivityTypes,
        **kwargs: dict[str, any],
    ) -> InsertOneResult | InsertManyResult:
        """Adds an activity.

        Args:
            user_id (int): _description_
            guild_id (int): _description_
            activity_type (ActivityTypes): _description_

        Returns:
            InsertOneResult | InsertManyResult: _description_
        """
        doc = {"uid": user_id, "guild_id": guild_id, "type": activity_type, "timestamp": datetime.datetime.now()}

        doc.update(kwargs)
        self.insert(doc)

    def get_guild_activities_by_timestamp(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> list[ActivityDB]:
        """Get guild activities between two timestamps.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): start time
            end (datetime.datetime): end time

        Returns:
            list[Activity]: activities between those times
        """
        return [
            self.make_data_class(act)
            for act in self.query({"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}}, limit=10000)
        ]

    def get_all_guild_activities(self, guild_id: int) -> list[ActivityDB]:
        """Get all activities for the given guild ID.

        Args:
            guild_id (int): the guild ID

        Returns:
            list[Activity]: the activities
        """
        return [self.make_data_class(act) for act in self.query({"guild_id": guild_id}, limit=10000)]
