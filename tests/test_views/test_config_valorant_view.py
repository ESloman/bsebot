"""Tests our Valorant Config views."""

from unittest import mock

import pytest

from discordbot.views.config_valorant import ValorantConfigView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestValorantConfigView:
    """Tests our ValorantConfigView view."""

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self, guild_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ValorantConfigView(guild_data["guild_id"])

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_cancel_callback(self, guild_data: dict[str, any]) -> None:
        """Tests cancel callback."""
        view = ValorantConfigView(guild_data["guild_id"])
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"])
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @pytest.mark.parametrize("active", ["1", "0"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_update(self, guild_data: dict[str, any], active: str) -> None:
        """Tests update method."""
        view = ValorantConfigView(guild_data["guild_id"])
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"])

        interaction.data["values"] = [active]
        view.active_select.refresh_state(interaction)
        await view.update(interaction)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @pytest.mark.parametrize("active", ["1", "0"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, guild_data: dict[str, any], active: str) -> None:
        """Tests the submit callback."""
        view = ValorantConfigView(guild_data["guild_id"])
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"])

        interaction.data["values"] = [active]
        view.active_select.refresh_state(interaction)
        await view.submit_callback.callback(interaction)
