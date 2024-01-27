"""Tests our eddie gains task."""

import pytest

from discordbot.tasks.activitychanger import ActivityChanger
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestEddieGainMessager:
    """Tests our EddieGainMessager class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = ActivityChanger(self.bsebot, [], self.logger, [], start=False)

    @pytest.mark.asyncio()
    async def test_execution_default(self) -> None:
        """Tests running the task with the default activity."""
        ActivityChanger(self.bsebot, [], self.logger, [], start=False)
