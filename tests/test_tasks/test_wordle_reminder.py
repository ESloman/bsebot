"""Tests our wordle reminder task."""


import pytest
from freezegun import freeze_time

from discordbot.tasks.wordlereminder import WordleReminder
from discordbot.utilities import PlaceHolderLogger
from tests.mocks import bsebot_mocks


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
