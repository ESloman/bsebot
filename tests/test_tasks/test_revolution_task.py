"""Tests our revolution task."""

import copy
import datetime
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from discordbot.tasks.revolutiontask import RevolutionTask
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

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_init(self) -> None:
        """Tests if we can initialise the task with empty data."""
        task = RevolutionTask(self.bsebot, [])
        assert not task.task.is_running()
        task = RevolutionTask(self.bsebot, [], start=True)
        assert task.task.is_running()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_init_with_guilds(self) -> None:
        """Tests if we can initialise the task with guild ids."""
        guild_ids = [guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})]
        _ = RevolutionTask(self.bsebot, guild_ids, "")

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_send_excited_gif(self, event_data: dict) -> None:
        """Tests send excited gif."""
        task = RevolutionTask(self.bsebot, [])
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
        task = RevolutionTask(self.bsebot, [])
        _event = RevolutionEvent.make_data_class(event_data)
        with mock.patch.object(task.giphy_api, "random_gif"):
            await task.create_event(_event.guild_id, _event, Guilds.make_data_class(guild))

    @freeze_time("2024/01/01 12:00")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_default_execution_wrong_time(self) -> None:
        """Tests we exit out of default execution with wrong time."""
        task = RevolutionTask(self.bsebot, [])
        for key in task.rev_started:
            task.rev_started[key] = False
        await task.revolution()

    @pytest.mark.parametrize("timestamp", ["2024/01/21 16:00", "2024/01/21 16:01"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_default_execution_create(self, timestamp: str) -> None:
        """Tests default execution with creating the event."""
        task = RevolutionTask(self.bsebot, [])
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
        task = RevolutionTask(self.bsebot, [])
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
        task = RevolutionTask(self.bsebot, [])
        event_data = copy.deepcopy(event_data)
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

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {"success": True})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_handle_bribe_stuff_event_success(self, event_data: dict[str, any]) -> None:
        """Tests handle_bribe_stuff with success being True."""
        task = RevolutionTask(self.bsebot, [])
        event = RevolutionEvent.make_data_class(event_data)
        await task.handle_bribe_stuff(event, 0.0)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {"success": False})[-1:])
    @pytest.mark.parametrize("result", [25.0, 70.0])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_handle_bribe_stuff(self, event_data: dict[str, any], result: float) -> None:
        """Tests handle_bribe_stuff with success being True."""
        task = RevolutionTask(self.bsebot, [])
        event_data["chance"] = 60
        event = RevolutionEvent.make_data_class(event_data)
        with mock.patch.object(task.revolutions, "get_event", new=lambda *_: event):  # noqa: PT008
            await task.handle_bribe_stuff(event, result)

    @pytest.mark.parametrize("event_data", interface_mocks.query_mock("ticketedevents", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_resolve_revolution_no_users(self, event_data: dict) -> None:
        """Tests resolve revolutions with no users."""
        task = RevolutionTask(self.bsebot, [])

        event_data = copy.deepcopy(event_data)
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
        task = RevolutionTask(self.bsebot, [])

        event_data = copy.deepcopy(event_data)
        event_data["chance"] = 0
        if not event_data.get("revolutionaries", []):
            event_data["revolutionaries"] = event_data["users"]
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
        task = RevolutionTask(self.bsebot, [])

        event_data = copy.deepcopy(event_data)
        event_data["chance"] = 100
        if not event_data.get("revolutionaries", []):
            event_data["revolutionaries"] = event_data["users"]
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
    async def test_resolve_revolution_with_accepted_bribe(self, event_data: dict) -> None:
        """Tests resolve revolution with a bribe."""
        task = RevolutionTask(self.bsebot, [])

        event_data = copy.deepcopy(event_data)
        event_data["chance"] = 100
        event_data["bribe_accepted"] = True
        event_data["bribe_offered"] = True
        if not event_data.get("revolutionaries", []):
            event_data["revolutionaries"] = event_data["users"]
        event = RevolutionEvent.make_data_class(event_data)
        task.rev_started[event.guild_id] = True

        with (
            mock.patch.object(task.giphy_api, "random_gif"),
        ):
            await task.resolve_revolution(event.guild_id, event)
