"""Tests our highscore view."""

from unittest import mock

import discord
import pytest

from discordbot.selects.autogenerate import AutoBetsSelect, BetsAmountSelect
from discordbot.slashcommandeventclasses.autogenerate import AutoGenerate
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.autogenerate import AutoGenerateView
from tests.mocks import bsebot_mocks, discord_mocks


class TestHighscoreView:
    """Tests our Highscore view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.auto = AutoGenerate(self.bsebot, [], self.logger)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = AutoGenerateView(self.auto)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = AutoGenerateView(self.auto)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    async def test_update_first_page(self) -> None:
        """Tests update first page."""
        view = AutoGenerateView(self.auto)
        view._update_first_page()
        for child in view.children:
            if type(child) == discord.ui.Button and child.label == "Next":
                assert child.disabled

    async def test_update_first_page_without_timeout(self) -> None:
        """Tests update first page with no timeout."""
        view = AutoGenerateView(self.auto)
        view.data.pop("timeout")
        view._update_first_page()
        for child in view.children:
            if type(child) == discord.ui.Button and child.label == "Next":
                assert child.disabled

    async def test_update_first_page_with_data(self) -> None:
        """Tests update first page with all data present."""
        view = AutoGenerateView(self.auto)
        view.data["channel"] = 123456
        view.data["type"] = "valorant"
        view._update_first_page()
        for child in view.children:
            if type(child) == discord.ui.Button and child.label == "Next":
                assert not child.disabled

    @pytest.mark.parametrize("select", [True, False])
    async def test_update_second_page_random_no_amount_select(self, select: bool) -> None:
        """Tests update second page."""
        view = AutoGenerateView(self.auto)

        # set data
        view.amount_select = None
        view.bets_select = AutoBetsSelect("valorant") if select else None
        view.data["type"] = "valorant"
        view.data["method"] = "random"

        view._update_second_page()
        assert view.bets_select is None
        assert view.amount_select is not None

    @pytest.mark.parametrize("select", [True, False])
    async def test_update_second_page_selected_no_bet_select(self, select: bool) -> None:
        """Tests update second page."""
        view = AutoGenerateView(self.auto)

        # set data
        view.amount_select = BetsAmountSelect() if select else None
        view.bets_select = None
        view.data["type"] = "valorant"
        view.data["method"] = "selected"

        view._update_second_page()
        assert view.bets_select is not None
        assert view.amount_select is None

    @pytest.mark.parametrize("method", ["random", "selected"])
    async def test_update_second_page_without_data(self, method: str) -> None:
        """Tests update second page."""
        view = AutoGenerateView(self.auto)

        # set data
        view.data["type"] = "valorant"
        view.data["method"] = method
        view.amount_select = BetsAmountSelect()
        view.bets_select = AutoBetsSelect("valorant")

        view._update_second_page()

    @pytest.mark.parametrize("method", ["random", "selected"])
    async def test_update_second_page_with_data(self, method: str) -> None:
        """Tests update second page."""
        view = AutoGenerateView(self.auto)

        # set data
        view.data["type"] = "valorant"
        view.data["method"] = method
        view.data["number"] = 3
        view.data["_ids"] = [
            123456,
            654321,
        ]
        view.amount_select = BetsAmountSelect()
        view.bets_select = AutoBetsSelect("valorant")

        view._update_second_page()

    @pytest.mark.parametrize("number", [1, 2])
    async def test_update_method(self, number: int) -> None:
        """Tests update method."""
        view = AutoGenerateView(self.auto)

        view.current_page = number
        view.data["type"] = "valorant"
        view.data["method"] = "random"
        view.data["number"] = 3
        view.data["_ids"] = [123456, 654321]

        interaction = discord_mocks.InteractionMock(654321)
        await view.update(interaction)

    @pytest.mark.parametrize("number", [1, 2])
    async def test_submit_callback(self, number: int) -> None:
        """Tests submit callback method."""
        view = AutoGenerateView(self.auto)

        view.current_page = number

        interaction = discord_mocks.InteractionMock(654321)

        with mock.patch.object(self.auto, "autogenerate_wrapper") as auto_fn:
            await view.submit_callback.callback(interaction)
            assert auto_fn.call_count == (number - 1)
