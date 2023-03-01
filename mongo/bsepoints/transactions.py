import datetime

from pymongo.results import InsertOneResult, InsertManyResult

from discordbot.bot_enums import TransactionTypes
from mongo import interface
from mongo.datatypes import Transaction
from mongo.db_classes import BestSummerEverPointsDB


class UserTransactions(BestSummerEverPointsDB):
    """
    Class for interacting with the 'usertransactions' MongoDB collection in the 'bestsummereverpoints' DB
    """
    def __init__(self):
        """
        Constructor method that initialises the vault object
        """
        super().__init__()
        self._vault = interface.get_collection(self.database, "usertransactions")

    def add_transaction(
        self,
        user_id: int,
        guild_id: int,
        transaction_type: TransactionTypes,
        amount: int,
        **kwargs
    ) -> InsertOneResult | InsertManyResult:
        doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "type": transaction_type,
            "amount": amount,
            "timestamp": datetime.datetime.now()
        }

        doc.update(kwargs)
        self.insert(doc)

    def get_all_guild_transactions(self, guild_id: int) -> list[Transaction]:
        return self.query({"guild_id": guild_id}, limit=10000)
