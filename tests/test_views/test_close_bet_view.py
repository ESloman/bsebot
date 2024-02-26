"""Tests our close bet views."""

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.close import CloseABetView
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestCloseABetView:
    """Tests our CloseABetView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.close = CloseBet(self.bsebot, [], self.logger)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    async def test_init(self, user_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet_data = interface_mocks.query_mock("userbets", {"guild_id": user_data["guild_id"]})[-5:]
        bets = [UserBets.make_data_class(bet) for bet in bet_data]
        _ = CloseABetView(bets, self.close)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = CloseABetView([], self.close)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)
