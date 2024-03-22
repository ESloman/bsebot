"""Tests our bet amount select."""

import discord
import pytest

from discordbot.selects.betamount import BetAmountSelect
from discordbot.views.bseview import BSEView
from tests.mocks import discord_mocks


class TestBetAmountSelect:
    """Tests our BetAmountSelect select."""

    def _create_view(self, select: discord.ui.Select) -> discord.ui.View:
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

        # add our select
        view.add_item(select)
        return view

    @pytest.mark.parametrize("eddies", [0, 500, 256, 112, 5000, 657])
    async def test_init(self, eddies: int) -> None:
        """Tests basic init with some different eddies amounts.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        select = BetAmountSelect(eddies)
        if eddies:
            assert len(select.options) > len(select.min_amounts)
        else:
            assert len(select.options) == 1

    async def test_callback(self):
        """Tests callback method."""
        eddies = 500
        select = BetAmountSelect(eddies)
        _ = self._create_view(select)
        interaction = discord_mocks.InteractionMock()

        # force our select to have data
        interaction.data["values"] = [str(eddies / 2)]
        select.refresh_state(interaction)

        await select.callback(interaction)
        for option in select.options:
            if option.value == str(eddies / 2):
                assert option.default
            else:
                assert not option.default
