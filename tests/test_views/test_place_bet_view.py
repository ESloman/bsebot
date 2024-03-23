"""Tests our place views."""

import pytest

from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.views.place import PlaceABetView
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestPlaceABetView:
    """Tests our PlaceABetView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.place = PlaceBet(self.bsebot, [])

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-10:])
    async def test_init(self, user_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet_data = interface_mocks.query_mock("userbets", {"guild_id": user_data["guild_id"]})[-5:]
        bets = [UserBets.make_data_class(bet) for bet in bet_data]
        _ = PlaceABetView(bets, user_data["points"], self.place)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        bet_data = interface_mocks.query_mock("userbets", {})[-5:]
        bets = [UserBets.make_data_class(bet) for bet in bet_data]
        view = PlaceABetView(bets, 1000, self.place)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)
