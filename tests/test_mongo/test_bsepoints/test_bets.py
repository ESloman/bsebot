"""Tests our UserBets class."""

import random
from unittest import mock

import pytest
from bson import ObjectId

from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB
from tests.mocks import interface_mocks, userbets_mocks

BET_CACHE: list[dict[str, any]] | None = None


def _get_bet_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global BET_CACHE  # noqa: PLW0603
    if BET_CACHE is None:
        BET_CACHE = list(interface_mocks.query_mock("userbets", {}))
    if not number:
        return BET_CACHE
    return random.choices(BET_CACHE, k=number)


class TestUserBets:
    """Tests our UserBets class."""

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
        data = _get_bet_data()
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

    @pytest.mark.parametrize(("bet", "exp"), userbets_mocks.user_bets_count_data())
    def test_count_eddies_for_bet(self, bet: BetDB, exp: int) -> None:
        """Tests UserBets count_eddies method."""
        user_bets = UserBets()
        count = user_bets.count_eddies_for_bet(bet)
        assert count == exp

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_bet_data() if "type" not in entry})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_get_all_active_bets(self, guild_id: int) -> None:
        """Tests UserBets get_all_active_bets method."""
        user_bets = UserBets()
        bets = user_bets.get_all_active_bets(guild_id)
        assert isinstance(bets, list)
        for bet in bets:
            assert isinstance(bet, BetDB)
            assert bet.active
            assert bet.guild_id == guild_id

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_bet_data() if "type" not in entry})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_get_all_inactive_pending_bets(self, guild_id: int) -> None:
        """Tests UserBets get_all_inactive_pending_bets method."""
        user_bets = UserBets()
        bets = user_bets.get_all_inactive_pending_bets(guild_id)
        assert isinstance(bets, list)
        for bet in bets:
            assert isinstance(bet, BetDB)
            assert not bet.active
            assert bet.result is None
            assert bet.guild_id == guild_id

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_bet_data() if "type" not in entry})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_get_all_pending_bets(self, guild_id: int) -> None:
        """Tests UserBets get_all_pending_bets method."""
        user_bets = UserBets()
        bets = user_bets.get_all_pending_bets(guild_id)
        assert isinstance(bets, list)
        for bet in bets:
            assert isinstance(bet, BetDB)
            assert bet.result is None
            assert bet.guild_id == guild_id

    @pytest.mark.parametrize(
        ("guild_id", "user_id"),
        {(entry["guild_id"], entry["uid"]) for entry in interface_mocks.query_mock("userpoints", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    def test_user_bets_get_user_pending_points(self, guild_id: int, user_id: int) -> None:
        """Tests UserBets get_user_pending_points method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets, "query", new=userbets_mocks.user_pending_points_query):
            points = user_bets.get_user_pending_points(user_id, guild_id)
        assert isinstance(points, int)

    @pytest.mark.parametrize(
        ("guild_id", "user_id"),
        {(entry["guild_id"], entry["uid"]) for entry in interface_mocks.query_mock("userpoints", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    def test_user_bets_get_all_pending_bets_for_user(self, guild_id: int, user_id: int) -> None:
        """Tests UserBets get_all_pending_bets_for_user method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets, "query", new=userbets_mocks.user_pending_points_query):
            bets = user_bets.get_all_pending_bets_for_user(user_id, guild_id)
        assert isinstance(bets, list)
        for bet in bets:
            assert isinstance(bet, BetDB)
            assert str(user_id) in bet.betters

    @pytest.mark.parametrize(
        ("guild_id", "bet_id"),
        # load list of entries dynamically
        {(entry["guild_id"], entry["bet_id"]) for entry in _get_bet_data(100) if "type" not in entry},
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

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_get_bet_empty(self) -> None:
        """Tests UserBets get_bet method with empty expected."""
        user_bets = UserBets()
        user_bet = user_bets.get_bet_from_id(123456, "0001")
        assert user_bet is None

    @pytest.mark.parametrize(
        ("guild_id", "user_id", "options"),
        # load list of entries dynamically
        [
            (entry["guild_id"], entry["user"], entry["option_dict"])
            for entry in _get_bet_data(100)
            if "type" not in entry
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_bets_create_bet(self, guild_id: int, user_id: int, options: dict[str, any]) -> None:
        """Tests UserBets create_new_bet method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets, "_get_new_bet_id", return_value="0001"):
            bet = user_bets.create_new_bet(guild_id, user_id, "some title", list(options.keys()), options)
            assert bet.guild_id == guild_id
            assert bet.bet_id == "0001"
            assert bet.user == user_id

    @pytest.mark.parametrize(
        "bet_id",
        # load list of entries dynamically
        {entry["_id"] for entry in _get_bet_data(50)},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_bets_close_bet(self, bet_id: ObjectId) -> None:
        """Tests UserBets close_a_bet method."""
        user_bets = UserBets()
        user_bets.close_a_bet(bet_id, "")

    @pytest.mark.parametrize(
        "bet",
        [UserBets.make_data_class(entry) for entry in _get_bet_data(50) if "type" not in entry],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_bets_add_new_better_to_bet(self, bet: BetDB) -> None:
        """Tests UserBets _add_new_better_to_bet method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets.user_points, "increment_points", return_value=None) as inc_patch:
            if bet.users and bet.betters:
                user_id = bet.users[0]
                try:
                    emoji = bet.betters[str(user_id)].emoji
                except KeyError:
                    print(str(user_id))
                result = user_bets._add_new_better_to_bet(bet, user_id, emoji, 100)
                assert inc_patch.called
                assert isinstance(result, dict)
                assert result["success"]

            result = user_bets._add_new_better_to_bet(bet, 123456, "", 50)
            assert inc_patch.called
            assert isinstance(result, dict)
            assert result["success"]

    @pytest.mark.parametrize(
        "bet",
        [UserBets.make_data_class(entry) for entry in _get_bet_data(5) if "type" not in entry],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_add_new_better_to_bet_no_points(self, bet: BetDB) -> None:
        """Tests UserBets add_new_better_to_bet method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets.user_points, "get_user_points", return_value=5):
            user = 123456 if not bet.users else bet.users[0]
            result = user_bets.add_better_to_bet(bet.bet_id, bet.guild_id, user, "", 50)
            assert isinstance(result, dict)
            assert not result["success"]
            assert result["reason"] == "not enough points"

    @pytest.mark.parametrize(
        "bet",
        [UserBets.make_data_class(entry) for entry in _get_bet_data(5) if "type" not in entry],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_add_new_better_to_bet_not_existing(self, bet: BetDB) -> None:
        """Tests UserBets add_new_better_to_bet method."""
        user_bets = UserBets()
        with (
            mock.patch.object(user_bets.user_points, "get_user_points", return_value=500),
            mock.patch.object(user_bets, "_add_new_better_to_bet", return_value={"success": True}),
        ):
            user = 123456
            result = user_bets.add_better_to_bet(bet.bet_id, bet.guild_id, user, "", 50)
            assert isinstance(result, dict)
            assert result["success"]

    @pytest.mark.parametrize(
        "bet",
        [UserBets.make_data_class(entry) for entry in _get_bet_data(100) if entry.get("betters")],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_bets_add_new_better_to_bet_wrong_emoji(self, bet: BetDB) -> None:
        """Tests UserBets add_new_better_to_bet method."""
        user_bets = UserBets()
        with mock.patch.object(user_bets.user_points, "get_user_points", return_value=500):
            user = next(iter(bet.betters.keys()))
            emoji = ""
            result = user_bets.add_better_to_bet(bet.bet_id, bet.guild_id, user, emoji, 50)
            assert isinstance(result, dict)
            assert not result["success"]
            assert result["reason"] == "wrong option"

    @pytest.mark.parametrize(
        "bet",
        [UserBets.make_data_class(entry) for entry in _get_bet_data(50) if entry.get("betters")],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_bets_add_new_better_to_bet_success(self, bet: BetDB) -> None:
        """Tests UserBets add_new_better_to_bet method."""
        user_bets = UserBets()
        with (
            mock.patch.object(user_bets.user_points, "get_user_points", return_value=500),
            mock.patch.object(user_bets.user_points, "increment_points", return_value=None),
        ):
            user = next(iter(bet.betters.keys()))
            emoji = bet.betters[str(user)].emoji
            result = user_bets.add_better_to_bet(bet.bet_id, bet.guild_id, user, emoji, 50)
            assert isinstance(result, dict)
            assert result["success"]
