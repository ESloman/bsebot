from mongo import interface
from mongo.db_classes import BestSummerEverPointsDB


class UserPoints(BestSummerEverPointsDB):
    def __init__(self):
        super().__init__()
        self._vault = interface.get_collection(self.database, "userpoints")

    def find_user(self, user_id, guild_id):
        ret = self.query({"uid": user_id, "guild_id": guild_id})
        if ret:
            return ret[0]
        return None

    def get_user_points(self, user_id, guild_id):
        ret = self.query({"uid": user_id, "guild_id": guild_id}, projection={"points": True})
        return ret[0]["points"]

    def get_all_users_for_guild(self, guild_id):
        ret = self.query({"guild_id": guild_id}, projection={"points": True, "uid": True})
        return ret

    def create_user(self, user_id, guild_id):
        user_doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "points": 10
        }
        self.insert(user_doc)
