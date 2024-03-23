"""Tests our close bet views."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
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

        self.close = CloseBet(self.bsebot, [])

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    async def test_init(self, user_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet_data = interface_mocks.query_mock("userbets", {"guild_id": user_data["guild_id"]})[-5:]
        bets = [UserBets.make_data_class(bet) for bet in bet_data]
        _ = CloseABetView(bets, self.close)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-1:])
    async def test_init_with_single_bet(self, guild_data: dict[str, any]) -> None:
        """Tests basic init with single bet.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet_data = interface_mocks.query_mock("userbets", {"guild_id": guild_data["guild_id"]})[-1]
        bets = [UserBets.make_data_class(bet_data)]
        _ = CloseABetView(bets, self.close)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = CloseABetView([], self.close)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    async def test_submit_callback(self) -> None:
        """Tests submit callback."""
        view = CloseABetView([], self.close)

        interaction = discord_mocks.InteractionMock(123456)
        interaction.data["values"] = ["0001"]
        view.bet_select.refresh_state(interaction)

        interaction.data["values"] = [":one:"]
        view.bet_outcome_select.refresh_state(interaction)

        with mock.patch.object(view.close, "close_bet") as close_fn:
            await view.submit_button_callback.callback(interaction)
            assert close_fn.call_count
