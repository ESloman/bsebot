"""Tests our pledge views."""

import pytest

from discordbot.utilities import PlaceHolderLogger
from discordbot.views.pledge import PledgeView
from tests.mocks import bsebot_mocks


class TestPledgeView:
    """Tests our PledgeView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = PledgeView()
