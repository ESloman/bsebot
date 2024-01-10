"""Tests our UserActivities class."""

import datetime
import random
from unittest import mock

import pytest

from discordbot.bot_enums import ActivityTypes
from mongo import interface
from mongo.bsepoints.activities import UserActivities
from mongo.datatypes.actions import ActivityDB
from tests.mocks import interface_mocks

ACTIVITY_CACHE: list[dict[str, any]] | None = None


def _get_activity_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global ACTIVITY_CACHE  # noqa: PLW0603
    if ACTIVITY_CACHE is None:
        ACTIVITY_CACHE = list(interface_mocks.query_mock("useractivities", {}))
    if not number:
        return ACTIVITY_CACHE
    return random.choices(ACTIVITY_CACHE, k=number)


class TestUserActivities:
    """Tests our UserActivities class."""

    def test_user_activities_init(self) -> None:
        """Tests UserActivities init."""
        activities = UserActivities()
        assert isinstance(activities, UserActivities)

    def test_activities_make_data_class(self) -> None:
        """Tests UserActivities make_data_class."""
        for activity in _get_activity_data():
            act_db = UserActivities.make_data_class(activity)
            assert isinstance(act_db, ActivityDB)

    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_activities_add_activity(self) -> None:
        """Tests UserActivities add_activity."""
        activities = UserActivities()
        activities.add_activity(123, 456, ActivityTypes.BSEDDIES_VIEW, extra="some extra data")

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_activity_data()})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_activities_get_all_activities(self, guild_id: int) -> None:
        """Tests UserActivities get_all_guild_activities."""
        activities = UserActivities()
        all_activities = activities.get_all_guild_activities(guild_id)
        assert isinstance(all_activities, list)
        for act in all_activities:
            assert isinstance(act, ActivityDB)
            assert act.guild_id == guild_id

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_activity_data()})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_activities_get_all_activities_timestamp(self, guild_id: int) -> None:
        """Tests UserActivities get_all_guild_activities_by_timestamp.

        Note: this test is basically the same as above. Our mock query doesn't do any timestamp
        validation. Even if it did, it wouldn't really be testing the database query. Can only
        test that the function converts the returned entries into dataclasses.
        """
        activities = UserActivities()
        all_activities = activities.get_guild_activities_by_timestamp(
            guild_id, datetime.datetime.now(), datetime.datetime.now()
        )
        assert isinstance(all_activities, list)
        for act in all_activities:
            assert isinstance(act, ActivityDB)
            assert act.guild_id == guild_id
