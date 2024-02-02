"""Tests our addoption modals."""

from unittest import mock

import pytest

from discordbot.modals.addoption import AddBetOption
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.bet import BetView
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestAddOption:
    """Tests our AddOption view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.view = BetView
        self.place = PlaceBet(self.bsebot, [], self.logger)
        self.close = CloseBet(self.bsebot, [], self.logger)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self, bet_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet = UserBets.make_data_class(bet_data)
        view = BetView(bet, self.place, self.close)
        _ = AddBetOption(bet, view, self.place, self.close, self.logger)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_add_option(self, bet_data: dict) -> None:
        """Tests basic adding an option.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet = UserBets.make_data_class(bet_data)
        view = BetView(bet, self.place, self.close)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)

        modal = AddBetOption(bet, view, self.place, self.close, self.logger)
        modal.bet_options.value = "another option"

        await modal.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    async def test_add_option_no_outcomes(self, bet_data: dict) -> None:
        """Tests basic adding an option with empty string."""
        bet = UserBets.make_data_class(bet_data)
        view = BetView(bet, self.place, self.close)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)

        modal = AddBetOption(bet, view, self.place, self.close, self.logger)
        modal.bet_options.value = ""

        await modal.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    async def test_add_option_too_many_outcomes(self, bet_data: dict) -> None:
        """Tests basic adding an option with too many outcomes."""
        bet = UserBets.make_data_class(bet_data)
        view = BetView(bet, self.place, self.close)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)

        modal = AddBetOption(bet, view, self.place, self.close, self.logger)
        modal.bet_options.value = "1\n2\n3\n4\n5\n6\n7\n8\n9\n10"

        await modal.callback(interaction)
