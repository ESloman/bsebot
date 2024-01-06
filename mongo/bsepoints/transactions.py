"""Transactions collection interface."""

import dataclasses
import datetime

from pymongo.results import InsertManyResult, InsertOneResult

from discordbot.bot_enums import TransactionTypes
from mongo import interface
from mongo.datatypes.actions import TransactionDB
from mongo.db_classes import BestSummerEverPointsDB


class UserTransactions(BestSummerEverPointsDB):
    """Class for interacting with the 'usertransactions' MongoDB collection in the 'bestsummereverpoints' DB."""

    def __init__(self) -> None:
        """Constructor method that initialises the vault object."""
        super().__init__()
        self._vault = interface.get_collection(self.database, "usertransactions")

    @staticmethod
    def make_data_class(transaction: dict) -> TransactionDB:
        """Convert the dict into a dataclass.

        Args:
            transaction (dict): the transaction dict

        Returns:
            TransactionDB: the dataclass.
        """
        cls_fields = {f.name for f in dataclasses.fields(TransactionDB)}
        extras = {k: v for k, v in transaction.items() if k not in cls_fields}
        return TransactionDB(**{k: v for k, v in transaction.items() if k in cls_fields}, extras=extras)

    def add_transaction(
        self,
        user_id: int,
        guild_id: int,
        transaction_type: TransactionTypes,
        amount: int,
        **kwargs: dict[str, any],
    ) -> InsertOneResult | InsertManyResult:
        """Adds a transaction.

        Args:
            user_id (int): _description_
            guild_id (int): _description_
            transaction_type (TransactionTypes): _description_
            amount (int): _description_

        Returns:
            InsertOneResult | InsertManyResult: _description_
        """
        doc = {
            "uid": user_id,
            "guild_id": guild_id,
            "type": transaction_type,
            "amount": amount,
            "timestamp": datetime.datetime.now(),
        }

        doc.update(kwargs)
        self.insert(doc)

    def get_guild_transactions_by_timestamp(
        self,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
    ) -> list[TransactionDB]:
        """Get guild transactions between two timestamps.

        Args:
            guild_id (int): the guild ID
            start (datetime.datetime): start time
            end (datetime.datetime): end time

        Returns:
            list[Transaction]: transactions between those times
        """
        return [
            self.make_data_class(trans)
            for trans in self.query({"guild_id": guild_id, "timestamp": {"$gt": start, "$lt": end}}, limit=10000)
        ]

    def get_all_guild_transactions(self, guild_id: int) -> list[TransactionDB]:
        """Get all transactions for a given guild ID.

        Args:
            guild_id (int): the guild ID

        Returns:
            list[Transaction]: list of transactions
        """
        return [self.make_data_class(**trans) for trans in self.query({"guild_id": guild_id}, limit=10000)]
