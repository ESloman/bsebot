"""Tests our UserBets class."""

from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB
from tests.mocks import interface_mocks


class TestUserBets:
    """Tests our Guilds class."""

    def test_user_bets_init_defaults(self) -> None:
        """Tests UserBets init."""
        user_bets = UserBets()
        assert isinstance(user_bets, UserBets)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_bets_init_guilds(self) -> None:
        """Tests UserBets init with guilds."""
        user_bets = UserBets([123, 456])
        assert isinstance(user_bets, UserBets)

    def test_bets_make_data_class(self) -> None:
        """Tests UserBets make_data_class."""
        user_bets = UserBets()
        data = interface_mocks.query_mock("userbets", {})
        for entry in data:
            if "type" in entry:
                continue
            cls = user_bets.make_data_class(entry)
            assert isinstance(cls, BetDB)

    @pytest.mark.parametrize("query", [True, False])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_bets_create_counter_document(self, query: bool) -> None:
        """Tests UserBets _create_counter_document method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets, "query", return_value=query):
            user_bets._create_counter_document(123456)

    @pytest.mark.parametrize(("guild_id", "exp"), [(724395292912255056, "0581")])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_bets_get_new_bet_id(self, guild_id: int, exp: str) -> None:
        """Tests UserBets _get_new_bet_id method."""
        user_bets = UserBets()
        count = user_bets._get_new_bet_id(guild_id)
        assert count == exp

    @pytest.mark.parametrize(
        ("guild_id", "bet_id"),
        # load list of entries dynamically
        {
            (entry["guild_id"], entry["bet_id"])
            for entry in interface_mocks.query_mock("userbets", {})
            if "type" not in entry
        },
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_get_bet(self, guild_id: int, bet_id: int) -> None:
        """Tests UserBets get_bet method."""
        user_bets = UserBets()
        user_bet = user_bets.get_bet_from_id(guild_id, bet_id)
        assert isinstance(user_bet, BetDB)
        assert user_bet.guild_id == guild_id
        assert user_bet.bet_id == bet_id
