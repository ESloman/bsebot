"""Tests our revolution task."""

import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import pytest

from discordbot.tasks.revolutionbribestask import RevolutionBribeTask
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestBSEddiesRevolutionTask:
    """Tests our BSEddiesRevolutionTask class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task with empty data."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        assert not task.task.is_running()
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [], start=True)
        assert task.task.is_running()

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_king_times(self, guild_data: dict[str, any]) -> None:
        """Tests our get_king_times method."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        king_times = task._get_king_times(guild)
        assert isinstance(king_times, dict)
        assert len(king_times.keys())

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_guild_bribe_conditions_no_revolution(self, guild_data: dict[str, any]) -> None:
        """Tests guild bribe conditions with revolution not set."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild_data["revolution"] = False
        guild_db = Guilds.make_data_class(guild_data)
        assert not task._check_guild_bribe_conditions(guild_db, [])

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_guild_bribe_conditions_no_open_events(self, guild_data: dict[str, any]) -> None:
        """Tests guild bribe conditions with no open events."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild_data["revolution"] = True
        guild_db = Guilds.make_data_class(guild_data)
        assert not task._check_guild_bribe_conditions(guild_db, [])

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_guild_bribe_conditions_king_too_long(self, guild_data: dict[str, any]) -> None:
        """Tests guild bribe conditions with a long king."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild_data["revolution"] = True
        guild_data["king_since"] = datetime.datetime.now(tz=ZoneInfo("UTC")) - datetime.timedelta(days=45)
        events = [
            RevolutionEvent.make_data_class(event)
            for event in interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1:]
        ]
        guild_db = Guilds.make_data_class(guild_data)
        assert not task._check_guild_bribe_conditions(guild_db, events)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_guild_bribe_conditions(self, guild_data: dict[str, any]) -> None:
        """Tests guild bribe conditions with a long king."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild_data["revolution"] = True
        guild_data["king_since"] = datetime.datetime.now(tz=ZoneInfo("UTC")) - datetime.timedelta(minutes=5)
        events = [
            RevolutionEvent.make_data_class(event)
            for event in interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1:]
        ]
        guild_db = Guilds.make_data_class(guild_data)
        assert task._check_guild_bribe_conditions(guild_db, events)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_event_bribe_conditions_chance(self, guild_data: dict[str, any]) -> None:
        """Tests event bribe conditions with too low a chance."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        event["chance"] = 30
        event_db = RevolutionEvent.make_data_class(event)
        assert not task._check_event_bribe_conditions(event_db)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_event_bribe_conditions_saved(self, guild_data: dict[str, any]) -> None:
        """Tests event bribe conditions with a few save attempts."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        event["chance"] = 90
        event["times_saved"] += 1
        event_db = RevolutionEvent.make_data_class(event)
        assert not task._check_event_bribe_conditions(event_db)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    def test_event_bribe_conditions(self, guild_data: dict[str, any]) -> None:
        """Tests event bribe conditions."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        event["chance"] = 90
        event["times_saved"] = 0
        event_db = RevolutionEvent.make_data_class(event)
        assert task._check_event_bribe_conditions(event_db)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_bribe_conditions_guild_check_fail(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions with guild check fail."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])

        with mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: False):  # noqa: PT008
            assert not task._check_bribe_conditions(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_bribe_conditions_event_check_fail(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions with event fail."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        with (
            mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task, "_check_event_bribe_conditions", new=lambda _: False),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
        ):
            assert not task._check_bribe_conditions(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_bribe_conditions_different_king_fail(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions with a different king fail."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        users = interface_mocks.query_mock("userpoints", {"guild_id": guild_data["guild_id"]})
        for user in users:
            if user["uid"] == guild_data["king"]:
                user["points"] = 1
        users = [UserPoints.make_data_class(user) for user in users]

        with (
            mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task, "_check_event_bribe_conditions", new=lambda _: True),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
            mock.patch.object(task.user_points, "get_all_users_for_guild", new=lambda *_: users),  # noqa: PT008
        ):
            assert not task._check_bribe_conditions(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_bribe_conditions_save_cost_fail(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions where the king can afford to save thyself."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        users = interface_mocks.query_mock("userpoints", {"guild_id": guild_data["guild_id"]})
        for user in users:
            if user["uid"] != guild_data["king"]:
                user["points"] = 1
        users = [UserPoints.make_data_class(user) for user in users]

        with (
            mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task, "_check_event_bribe_conditions", new=lambda _: True),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
            mock.patch.object(task.user_points, "get_all_users_for_guild", new=lambda *_: users),  # noqa: PT008
        ):
            assert not task._check_bribe_conditions(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[-1:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_bribe_conditions_king_times_fail(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions where the king can afford to save thyself."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        users = interface_mocks.query_mock("userpoints", {"guild_id": guild_data["guild_id"]})
        king_user = next(user for user in users if user["uid"] == guild_data["king"])
        for user in users:
            if user["uid"] != guild_data["king"]:
                user["points"] = king_user["points"] - (2 + users.index(user))
        users = [UserPoints.make_data_class(user) for user in users]

        with (
            mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task, "_check_event_bribe_conditions", new=lambda _: True),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
            mock.patch.object(task.user_points, "get_all_users_for_guild", new=lambda *_: users),  # noqa: PT008
        ):
            assert not task._check_bribe_conditions(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])[:1]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_bribe_conditions_pass(self, guild_data: dict[str, any]) -> None:
        """Tests bribe conditions where we succeed."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        guild = discord_mocks.GuildMock(guild_data["guild_id"])
        event = interface_mocks.query_mock("ticketedevents", {"guild_id": guild_data["guild_id"]})[-1]
        users = interface_mocks.query_mock("userpoints", {"guild_id": guild_data["guild_id"]})
        king_user = next(user for user in users if user["uid"] == guild_data["king"])
        users = [UserPoints.make_data_class(user) for user in users]

        king_times = {user.uid: 1000 for user in users}
        king_times[king_user["uid"]] = 100

        with (
            # so many mocks!
            mock.patch.object(task, "_check_guild_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task, "_check_event_bribe_conditions", new=lambda _: True),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
            mock.patch.object(task.user_points, "get_all_users_for_guild", new=lambda *_: users),  # noqa: PT008
            mock.patch.object(task, "_get_king_times", new=lambda *_: king_times),  # noqa: PT008
        ):
            assert task._check_bribe_conditions(guild)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_bribe_conditions_false(self) -> None:
        """Tests bribe where the conditions are false."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        with (
            mock.patch.object(task, "_check_bribe_conditions", new=lambda *_: False),  # noqa: PT008
        ):
            assert task.bribe()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_bribe(self) -> None:
        """Tests bribe execution."""
        task = RevolutionBribeTask(self.bsebot, [], self.logger, [])
        event = interface_mocks.query_mock("ticketedevents", {})[-1]
        with (
            mock.patch.object(task, "_check_bribe_conditions", new=lambda *_: True),  # noqa: PT008
            mock.patch.object(task.revolutions, "get_open_events", return_val=[RevolutionEvent.make_data_class(event)]),
        ):
            assert task.bribe()
