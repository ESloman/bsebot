"""Tests our stats views."""

import pytest

from discordbot.slashcommandeventclasses.stats import Stats
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.stats import StatsView
from tests.mocks import bsebot_mocks


class TestStatsView:
    """Tests our StatsView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.stats = Stats(self.bsebot, [], self.logger)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = StatsView(self.stats)
