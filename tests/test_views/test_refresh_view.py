"""Tests our refresh views."""

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.refresh import RefreshBetView
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, interface_mocks


class TestRefreshBetView:
    """Tests our RefreshBetView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.place = PlaceBet(self.bsebot, [], self.logger)
        self.close = CloseBet(self.bsebot, [], self.logger)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-5:]]
        _ = RefreshBetView(bets, self.place, self.close)
