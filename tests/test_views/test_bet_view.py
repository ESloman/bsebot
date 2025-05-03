"""Tests our bet views."""

from unittest import mock

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.views.bet import BetView
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


@pytest.mark.xfail
class TestBetView:
    """Tests our BetView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.place = PlaceBet(self.bsebot)
        self.close = CloseBet(self.bsebot)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    async def test_init(self, bet_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet = UserBets.make_data_class(bet_data)
        _ = BetView(bet, self.place, self.close)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_place_callback(self, bet_data: dict) -> None:
        """Tests place callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        with mock.patch.object(view.place, "create_bet_view"):
            await view.place_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_close_callback(self, bet_data: dict) -> None:
        """Tests close callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        with mock.patch.object(view.close, "create_bet_view"):
            await view.close_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_cancel_callback(self, bet_data: dict) -> None:
        """Tests cancel callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        with mock.patch.object(view.close, "cancel_bet"):
            await view.cancel_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_add_callback(self, bet_data: dict) -> None:
        """Tests add callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        await view.add_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_add_callback_bad_user(self, bet_data: dict) -> None:
        """Tests add callback with a different user ID."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, 123456)
        view = BetView(bet, self.place, self.close)

        await view.add_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_add_callback_with_open_bets(self, bet_data: dict) -> None:
        """Tests add callback with definitely open bets."""
        bet_data["active"] = True
        bet_data["closed"] = True
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        await view.add_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_change_callback(self, bet_data: dict) -> None:
        """Tests change callback."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        await view.change_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_change_callback_bad_user(self, bet_data: dict) -> None:
        """Tests change callback with a user ID that hasn't bet on the bet."""
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, 123456)
        view = BetView(bet, self.place, self.close)

        await view.change_callback.callback(interaction)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_change_callback_with_open_bets(self, bet_data: dict) -> None:
        """Tests change callback with definitely open bets."""
        bet_data["active"] = True
        bet_data["closed"] = True
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        view = BetView(bet, self.place, self.close)

        await view.change_callback.callback(interaction)
