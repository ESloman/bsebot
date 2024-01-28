"""Tests our guild checker task."""

import pytest

from discordbot.tasks.guildchecker import GuildChecker
from discordbot.utilities import PlaceHolderLogger
from tests.mocks import bsebot_mocks, slashcommand_mocks


class TestActivityChanger:
    """Tests our ActivityChanger class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.close = slashcommand_mocks.CloseABetMock(self.bsebot, [], self.logger)
        self.place = slashcommand_mocks.PlaceABetMock(self.bsebot, [], self.logger)

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
