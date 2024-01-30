"""Tests our revolution task."""

import datetime
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from discordbot.tasks.revolutiontask import BSEddiesRevolutionTask
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import bsebot_mocks, interface_mocks


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
        _ = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_init_with_guilds(self) -> None:
        """Tests if we can initialise the task with guild ids."""
        guild_ids = [guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})]
        _ = BSEddiesRevolutionTask(self.bsebot, guild_ids, self.logger, [], "", start=False)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_send_excited_gif(self, event_data: dict) -> None:
        """Tests send excited gif."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)
        _event = RevolutionEvent.make_data_class(event_data)
        with mock.patch.object(task.giphy_api, "random_gif"):
            await task.send_excited_gif(_event, "2 hours", "two_hours")

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_create_event(self, event_data: dict) -> None:
        """Tests create event message."""
        guild = interface_mocks.query_mock("guilds", {"guild_id": event_data["guild_id"]})[0]
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)
        _event = RevolutionEvent.make_data_class(event_data)
        with mock.patch.object(task.giphy_api, "random_gif"):
            await task.create_event(_event.guild_id, _event, Guilds.make_data_class(guild))

    @freeze_time("2024/01/01 12:00")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_default_execution_wrong_time(self) -> None:
        """Tests we exit out of default execution with wrong time."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)
        await task.revolution()

    @pytest.mark.parametrize("timestamp", ["2024/01/21 16:00", "2024/01/21 16:01"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_default_execution_create(self, timestamp: str) -> None:
        """Tests default execution with creating the event."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)
        with freeze_time(timestamp), mock.patch.object(task.giphy_api, "random_gif"):
            await task.revolution()

    @freeze_time("2024/01/21 16:01")
    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-2:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_default_execution_started(self, event_data: dict) -> None:
        """Tests default execution when the event has been started."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)
        event = RevolutionEvent.make_data_class(event_data)
        task.rev_started[event.guild_id] = True
        with (
            mock.patch.object(task.giphy_api, "random_gif"),
            mock.patch.object(task.revolutions, "get_open_events", return_value=[event]),
            mock.patch.object(task, "resolve_revolution"),
        ):
            await task.revolution()

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-2:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_default_execution_reminders(self, event_data: dict) -> None:
        """Tests default execution with the reminders for the event."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)

        event_data["one_hour"] = False
        event_data["quarter_hour"] = False
        for timestamp in ("2024/01/21 18:00", "2024/01/21 18:30", "2024/01/21 19:15"):
            with freeze_time(timestamp):
                event_data["expired"] = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(hours=1)
                event = RevolutionEvent.make_data_class(event_data)
                task.rev_started[event.guild_id] = True

                with (
                    mock.patch.object(task.giphy_api, "random_gif"),
                    mock.patch.object(task.revolutions, "get_open_events", return_value=[event]),
                    mock.patch.object(task, "resolve_revolution"),
                ):
                    await task.revolution()

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_resolve_revolution_no_users(self, event_data: dict) -> None:
        """Tests resolve revolutions with no users."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)

        event_data["users"] = []
        event = RevolutionEvent.make_data_class(event_data)
        task.rev_started[event.guild_id] = True

        with (
            mock.patch.object(task.giphy_api, "random_gif"),
        ):
            await task.resolve_revolution(event.guild_id, event)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_resolve_revolution_not_success(self, event_data: dict) -> None:
        """Tests resolve revolutions that doesn't succeed."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)

        event_data["chance"] = 0
        event = RevolutionEvent.make_data_class(event_data)
        task.rev_started[event.guild_id] = True

        with (
            mock.patch.object(task.giphy_api, "random_gif"),
        ):
            await task.resolve_revolution(event.guild_id, event)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_resolve_revolution_success(self, event_data: dict) -> None:
        """Tests resolve revolutions that succeeds."""
        task = BSEddiesRevolutionTask(self.bsebot, [], self.logger, [], "", start=False)

        event_data["chance"] = 100
        if not event_data.get("revolutionaries", []):
            event_data["revolutionaries"] = event_data["users"]
        event = RevolutionEvent.make_data_class(event_data)
        task.rev_started[event.guild_id] = True

        with (
            mock.patch.object(task.giphy_api, "random_gif"),
        ):
            await task.resolve_revolution(event.guild_id, event)
