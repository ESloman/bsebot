"""Tests our UserPoints class."""

from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.user import UserDB
from tests.mocks import interface_mocks


class TestUserPoints:
    """Tests our BaseClass class."""

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
        [(entry["uid"], entry["guild_id"]) for entry in interface_mocks.query_mock("userpoints", {})],
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
        user = user_points.find_user(user_id=user_id, guild_id=guild_id)
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
