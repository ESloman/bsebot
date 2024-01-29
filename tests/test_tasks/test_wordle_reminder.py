"""Tests our wordle reminder task."""

from unittest import mock

import pytest
from freezegun import freeze_time

from discordbot.tasks.wordlereminder import WordleReminder
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from tests.mocks import bsebot_mocks, interface_mocks


class TestWordleReminder:
    """Tests our WordleReminder class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = WordleReminder(self.bsebot, [], self.logger, [], start=False)

    @freeze_time("2024/01/29 13:00")
    async def test_default_execution(self) -> None:
        """Tests that we don't trigger on the wrong time."""
        task = WordleReminder(self.bsebot, [], self.logger, [], start=False)
        await task.wordle_reminder()

    @freeze_time("2024/01/01 19:30")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_default_execution_no_reminders(self) -> None:
        """Tests execution with a day that had wordles done successfully."""
        task = WordleReminder(self.bsebot, [], self.logger, [], start=False)
        await task.wordle_reminder()
