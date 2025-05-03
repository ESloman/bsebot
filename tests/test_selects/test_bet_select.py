"""Tests our bet selects."""

from unittest import mock

import discord
import pytest

from discordbot.selects.bet import BetSelect
from discordbot.selects.betamount import BetAmountSelect
from discordbot.selects.betoutcomes import BetOutcomesSelect
from discordbot.views.bseview import BSEView
from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB
from tests.mocks import discord_mocks, interface_mocks


class TestBetSelect:
    """Tests our BetSelect select."""

    def _create_view(self, select: discord.ui.Select, bet_db: BetDB | None = None) -> discord.ui.View:
        """Creates a view for testing.

        Adds the select to the view so the select has a parent.

        Args:
            select (discord.ui.Select): the select we're creating

        Returns:
            discord.ui.View: the created View
        """
        view = BSEView()
        for label in ("Submit", "Cancel"):
            button = discord.ui.Button(label=label)
            view.add_item(button)

        # add the amount select
        amount_select = BetAmountSelect(3000)
        view.add_item(amount_select)

        # add the bet outcome select
        if bet_db:
            options = [
                discord.SelectOption(label=bet_db.option_dict[key].val, value=key, emoji=key)
                for key in bet_db.option_dict
            ]
        else:
            options = []
        outcome_select = BetOutcomesSelect(options)
        view.add_item(outcome_select)

        # add our select
        view.add_item(select)
        return view

    @pytest.mark.xfail
    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-10:]]
        select = BetSelect(bets)
        assert len(select.options) == len(bets)

    @pytest.mark.xfail
    async def test_init_with_one_bet(self) -> None:
        """Tests basic init with one bet.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-1:]]
        select = BetSelect(bets)
        assert select.options[0].default

    async def test_init_with_some_long_titles(self) -> None:
        """Tests basic init with some long titles.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bet_data = interface_mocks.query_mock("userbets", {})[-5:]
        bets = []
        for bet in bet_data:
            bet["title"] += "some random long string so that we can have some really long bet titles that get truncated"
            bets.append(UserBets.make_data_class(bet))
        select = BetSelect(bets)
        assert len(select.options) == len(bets)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    async def test_enable_outcome_select(self, bet_data: dict[str, any]) -> None:
        """Tests _disable_submit_button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-10:]]
        select = BetSelect(bets)
        view = self._create_view(select)

        selected_bet = UserBets.make_data_class(bet_data)
        outcome_select = next(item for item in view.children if type(item) is BetOutcomesSelect)
        select._enable_outcome_select(outcome_select, selected_bet)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_callback(self, bet_data: dict[str, any]) -> None:
        """Tests _disable_submit_button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-10:]]
        select = BetSelect(bets)
        _ = self._create_view(select)
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)

        # force our select to have data
        interaction.data["values"] = [str(bet.bet_id)]
        select.refresh_state(interaction)

        await select.callback(interaction)
