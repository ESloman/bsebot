import datetime

from pymongo.results import InsertOneResult, InsertManyResult

from discordbot.bot_enums import ActivityTypes
from mongo import interface
from mongo.datatypes import Activity
from mongo.db_classes import BestSummerEverPointsDB


class UserActivities(BestSummerEverPointsDB):
    """
    Class for interacting with the 'useractivities' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method that initialises the vault object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "useractivities")

    def add_activity(
        self,
        user_id: int,
        guild_id: int,
        activity_type: ActivityTypes,
        **kwargs
    ) -> InsertOneResult | InsertManyResult:
        doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "type": activity_type,
            "timestamp": datetime.datetime.now()
        }

        doc.update(kwargs)
        self.insert(doc)

    def get_all_guild_activities(self, guild_id: int) -> list[Activity]:
        return self.query({"guild_id": guild_id}, limit=10000)
