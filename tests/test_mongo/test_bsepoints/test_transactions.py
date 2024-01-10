"""Tests our UserTransactions class."""

import datetime
import random
from unittest import mock

import pytest

from discordbot.bot_enums import TransactionTypes
from mongo import interface
from mongo.bsepoints.transactions import UserTransactions
from mongo.datatypes.actions import TransactionDB
from tests.mocks import interface_mocks

TRANSACTION_CACHE: list[dict[str, any]] | None = None


def _get_transaction_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global TRANSACTION_CACHE  # noqa: PLW0603
    if TRANSACTION_CACHE is None:
        TRANSACTION_CACHE = list(interface_mocks.query_mock("usertransactions", {}))
    if not number:
        return TRANSACTION_CACHE
    return random.choices(TRANSACTION_CACHE, k=number)


class TestUserTransactions:
    """Tests our UserTransactions class."""

    def test_user_transactions_init(self) -> None:
        """Tests UserTransactions init."""
        transactions = UserTransactions()
        assert isinstance(transactions, UserTransactions)

    def test_transactions_make_data_class(self) -> None:
        """Tests UserTransactions make_data_class."""
        for transaction in _get_transaction_data():
            act_db = UserTransactions.make_data_class(transaction)
            assert isinstance(act_db, TransactionDB)

    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_transactions_add_transaction(self) -> None:
        """Tests UserTransactions add_transaction."""
        transactions = UserTransactions()
        transactions.add_transaction(123, 456, TransactionTypes.DAILY_SALARY, 50)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_transaction_data()})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_transactions_get_all_transactions(self, guild_id: int) -> None:
        """Tests UserTransactions get_all_guild_transactions."""
        transactions = UserTransactions()
        all_transactions = transactions.get_all_guild_transactions(guild_id)
        assert isinstance(all_transactions, list)
        for act in all_transactions:
            assert isinstance(act, TransactionDB)
            assert act.guild_id == guild_id

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_transaction_data()})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_transactions_get_all_transactions_timestamp(self, guild_id: int) -> None:
        """Tests UserTransactions get_all_guild_transactions_by_timestamp.

        Note: this test is basically the same as above. Our mock query doesn't do any timestamp
        validation. Even if it did, it wouldn't really be testing the database query. Can only
        test that the function converts the returned entries into dataclasses.
        """
        transactions = UserTransactions()
        all_transactions = transactions.get_guild_transactions_by_timestamp(
            guild_id, datetime.datetime.now(), datetime.datetime.now()
        )
        assert isinstance(all_transactions, list)
        for act in all_transactions:
            assert isinstance(act, TransactionDB)
            assert act.guild_id == guild_id
