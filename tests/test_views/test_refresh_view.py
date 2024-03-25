"""Tests our refresh views."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.views.refresh import RefreshBetView
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestRefreshBetView:
    """Tests our RefreshBetView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.place = PlaceBet(self.bsebot)
        self.close = CloseBet(self.bsebot)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-5:]]
        _ = RefreshBetView(bets, self.place, self.close)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_submit_callback_default(self) -> None:
        """Tests submit callback does what we want it to with the default bet."""
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-1:]]
        view = RefreshBetView(bets, self.place, self.close)
        interaction = discord_mocks.InteractionMock(bets[0].guild_id, bets[0].user)

        await view.submit_callback.callback(interaction)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_submit_callback_selected(self) -> None:
        """Tests submit callback does what we want it to with a chosen bet."""
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-5:]]
        view = RefreshBetView(bets, self.place, self.close)
        interaction = discord_mocks.InteractionMock(bets[1].guild_id, bets[1].user)

        # force our select to have data
        interaction.data["values"] = [f"{bets[1].bet_id}"]
        view.bet_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = RefreshBetView([], self.place, self.close)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)
