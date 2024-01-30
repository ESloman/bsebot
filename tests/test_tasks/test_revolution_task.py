"""Tests our revolution task."""

from unittest import mock

import pytest
from freezegun import freeze_time

from discordbot.tasks.revolutiontask import BSEddiesRevolutionTask
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
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
