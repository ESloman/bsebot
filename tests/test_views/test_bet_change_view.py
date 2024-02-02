"""Tests our bet change views."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.bet import BetView
from discordbot.views.betchange import BetChange
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestBetChange:
    """Tests our BetChange view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.place = PlaceBet(self.bsebot, [], self.logger)
        self.close = CloseBet(self.bsebot, [], self.logger)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    async def test_init(self, bet_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet = UserBets.make_data_class(bet_data)
        view = BetView(bet, self.place, self.close)
        _ = BetChange(bet, view, self.place, self.close)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_change_callback(self, bet_data: dict) -> None:
        """Tests change callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)
        change = BetChange(bet, view, self.place, self.close)

        # force our select to have data
        interaction.data["values"] = [bet.option_vals[0]]
        change.outcome_select.refresh_state(interaction)

        await change.submit_callback.callback(interaction)
