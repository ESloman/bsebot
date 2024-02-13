"""Tests our bet selects."""

from unittest import mock

import discord
import pytest

from discordbot.selects.bet import BetSelect
from discordbot.selects.betamount import BetSelectAmount
from discordbot.selects.betoutcomes import BetOutcomesSelect
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
        view = discord.ui.View()
        for label in ("Submit", "Cancel"):
            button = discord.ui.Button(label=label)
            view.add_item(button)

        # add the amount select
        amount_select = BetSelectAmount(3000)
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

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-10:]]
        _ = BetSelect(bets)

    async def test_enable_submit_button(self) -> None:
        """Tests _enable_submit_button.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        bets = [UserBets.make_data_class(bet) for bet in interface_mocks.query_mock("userbets", {})[-10:]]
        select = BetSelect(bets)
        view = self._create_view(select)
        select._enable_submit_button()
        buttons = [item for item in view.children if isinstance(item, discord.ui.Button)]
        for button in buttons:
            if button.label == "Submit":
                assert not button.disabled

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
