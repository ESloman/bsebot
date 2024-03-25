"""Tests our reminder task."""

import datetime
import random
from unittest import mock

import pytest
import pytz

from discordbot.tasks.reminders import RemindersTask
from mongo import interface
from mongo.bsepoints.reminders import ServerReminders
from tests.mocks import bsebot_mocks, interface_mocks


class TestRemindersTask:
    """Tests our RemindersTask class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = RemindersTask(self.bsebot, [], start=False)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_execution(self) -> None:
        """Tests default execution."""
        task = RemindersTask(self.bsebot, [], start=False)
        await task.reminders()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_execution_with_open_reminders(self) -> None:
        """Tests default execution with open reminedrs."""
        task = RemindersTask(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=pytz.utc)
        reminder_data = interface_mocks.query_mock("reminders", {})[-5:]
        for reminder in reminder_data:
            reminder["active"] = True
            reminder["timeout"] = now + datetime.timedelta(minutes=5 if random.random() > 0.5 else -5)
        reminders = [ServerReminders.make_data_class(r) for r in reminder_data]
        with mock.patch.object(task.server_reminders, "get_open_reminders", return_value=reminders):
            await task.reminders()
