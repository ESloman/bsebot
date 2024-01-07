"""Tests our UserPoints class."""

import random
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.user import UserDB
from tests.mocks import interface_mocks


class TestUserPoints:
    """Tests our UserPoints class."""

    def test_user_points_init(self) -> None:  # noqa: PLR6301
        """Tests UserPoints init."""
        user_points = UserPoints()
        assert isinstance(user_points, UserPoints)
        assert user_points.database is not None
        assert user_points.vault is not None
        assert user_points._MINIMUM_PROJECTION_DICT is not None
        for val in user_points._MINIMUM_PROJECTION_DICT.values():
            assert val is True

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})]
        + [
            (123456, 654321),
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_points_check_highest_eddie_count(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints _check_highest_eddie_count."""
        user_points = UserPoints()
        user_points._check_highest_eddie_count(user_id, guild_id)

    def test_user_points_make_data_class(self) -> None:  # noqa: PLR6301
        """Tests UserPoints make_data_class."""
        user_points = UserPoints()
        data = interface_mocks.query_mock("userpoints", {})
        for entry in data:
            cls = user_points.make_data_class(entry)
            assert isinstance(cls, UserDB)

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_find_user(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints find_user."""
        user_points = UserPoints()
        projection = {} if random.random() > 0.5 else None
        user = user_points.find_user(user_id=user_id, guild_id=guild_id, projection=projection)
        assert isinstance(user, UserDB)
        assert user.uid == user_id
        assert user.guild_id == guild_id

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [
            (123456, 654321),
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_find_user_none(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints find_user with a user that doesn't exist."""
        user_points = UserPoints()
        user = user_points.find_user(user_id=user_id, guild_id=guild_id)
        assert not isinstance(user, UserDB)
        assert user is None

    @pytest.mark.parametrize(
        "user_id",
        # load list of entries dynamically
        [entry["uid"] for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_find_user_guildless(self, user_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints find_user_guildless."""
        user_points = UserPoints()
        results = user_points.find_user_guildless(user_id=user_id)
        assert isinstance(results, list)
        for entry in results:
            assert isinstance(entry, UserDB)
            assert entry.uid == user_id

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_get_user_points(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints get_user_points."""
        user_points = UserPoints()
        points = user_points.get_user_points(user_id, guild_id)
        assert isinstance(points, int)

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_get_user_daily_minimum(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints get_user_daily_minimum."""
        user_points = UserPoints()
        points = user_points.get_user_daily_minimum(user_id, guild_id)
        assert isinstance(points, int)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("userpoints", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_get_users_for_guild(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints get_users_for_guild."""
        user_points = UserPoints()
        users = user_points.get_all_users_for_guild(guild_id)
        assert isinstance(users, list)
        assert len(users) > 0
        for user in users:
            assert isinstance(user, UserDB)
            assert user.guild_id == guild_id

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_points_set_daily_minimum(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints set_daily_minimum."""
        user_points = UserPoints()
        user_points.set_daily_minimum(user_id, guild_id, random.randint(0, 10))

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_increment_points(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints increment_points."""
        user_points = UserPoints()
        with mock.patch.object(user_points._trans, "add_transaction", return_value=None):
            user_points.increment_points(user_id, guild_id, random.randint(-10, 10), 0)

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_points_create_user(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints increment_points."""
        user_points = UserPoints()
        with mock.patch.object(user_points._trans, "add_transaction", return_value=None):
            user_points.create_user(user_id, guild_id, "some name", False)

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_points_set_daily_eddies_toggle(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints increment_points."""
        user_points = UserPoints()
        user_points.set_daily_eddies_toggle(user_id, guild_id, False)
        user_points.set_daily_eddies_toggle(user_id, 0, False)

    @pytest.mark.parametrize(
        ("user_id", "guild_id"),
        # load list of entries dynamically
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_points_set_king_flag(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints set_king_flag."""
        user_points = UserPoints()
        user_points.set_king_flag(user_id, guild_id, False)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("userpoints", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_get_current_king(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints get_current_king."""
        user_points = UserPoints()
        user = user_points.get_current_king(guild_id)
        assert isinstance(user, UserDB)
        assert user.king
