"""Tests our Salary Config views."""

from unittest import mock

import pytest

from discordbot.views.config_salary import SalaryConfigView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


@pytest.mark.xfail
class TestSalaryConfigView:
    """Tests our SalaryConfigView view."""

    @pytest.mark.parametrize("amount", [2, 3, 4, None])
    async def test_init(self, amount: int | None) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = SalaryConfigView(amount)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = SalaryConfigView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("guild_id", [guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})])
    @pytest.mark.parametrize("amount", [2, 3, 4, 5])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, guild_id: int, amount: int) -> None:
        """Tests the submit callback."""
        view = SalaryConfigView()

        interaction = discord_mocks.InteractionMock(guild_id)
        interaction.data["values"] = [str(amount)]
        view.min_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)
