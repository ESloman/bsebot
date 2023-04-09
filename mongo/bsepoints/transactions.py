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

    def get_guild_transactions_by_timestamp(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> list[Transaction]:
        """Get guild transactions between two timestamps

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): start time
            end (datetime.datetime): end time

        Returns:
            list[Transaction]: transactions between those times
        """
        return self.query(
            {"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}},
            limit=10000
        )

    def get_all_guild_transactions(self, guild_id: int) -> list[Transaction]:
        """Get all transactions for a given guild ID

        Args:
            guild_id (int): the guild ID

        Returns:
            list[Transaction]: list of transactions
        """
        return self.query({"guild_id": guild_id}, limit=10000)
