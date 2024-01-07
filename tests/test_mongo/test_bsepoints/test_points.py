"""Tests our UserPoints class."""

from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.points import UserPoints
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
        [
            (309833219350462464, 724395292912255056),
            (809505325505576971, 724395292912255056),
            (757743113262858240, 724395292912255056),
            (880530045314007040, 724395292912255056),
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_points_check_highest_eddie_count(self, user_id: int, guild_id: int) -> None:  # noqa: PLR6301
        """Tests UserPoints _check_highest_eddie_count."""
        user_points = UserPoints()
        user_points._check_highest_eddie_count(user_id, guild_id)
