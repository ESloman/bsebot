"""Tests our TaxRateView view."""

from unittest import mock

import pytest

from discordbot.views.taxrate import TaxRateView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestTaxRateView:
    """Tests our TaxRateView view."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = TaxRateView(0.2, 0.1)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = TaxRateView(0.2, 0.1)
        interaction = discord_mocks.InteractionMock(654321)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_submit_callback(self, guild_id: int) -> None:
        """Tests submit callback."""
        view = TaxRateView(0.2, 0.1)
        interaction = discord_mocks.InteractionMock(guild_id)

        await view.submit_callback.callback(interaction)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_submit_callback_with_no_guild(self) -> None:
        """Tests submit callback."""
        view = TaxRateView(0.2, 0.1)
        interaction = discord_mocks.InteractionMock(123456)

        await view.submit_callback.callback(interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_submit_callback_with_selected_data(self, guild_id: int) -> None:
        """Tests submit callback."""
        view = TaxRateView(0.2, 0.1)
        interaction = discord_mocks.InteractionMock(guild_id)

        # force our select to have data
        interaction.data["values"] = [0.5]
        view.tax_select.refresh_state(interaction)
        interaction.data["values"] = [0.25]
        view.supporter_tax_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)
