from mongo import interface
from mongo.baseclass import BaseClass


class BestSummerEverPointsDB(BaseClass):
    def __init__(self):
        super().__init__()
        self.bse_db = interface.get_database(self.cli, "bestsummereverpoints")

    @property
    def database(self):
        return self.bse_db
