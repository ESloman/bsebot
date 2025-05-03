"""Tests our Admin Config views."""

from unittest import mock

import pytest

from discordbot.views.config_admin import AdminConfigView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


@pytest.mark.xfail
class TestAdminConfigView:
    """Tests our AdminConfigView view."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = AdminConfigView()

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = AdminConfigView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    async def test_update(self) -> None:
        """Tests update method."""
        view = AdminConfigView()
        interaction = discord_mocks.InteractionMock(123456)
        values = [discord_mocks.MemberMock(123456 + x) for x in range(3)]
        interaction.data["values"] = values
        view.admins_select.refresh_state(interaction)

        with mock.patch("discord.ui.Select.values", new_callable=mock.PropertyMock, return_value=values):
            await view.update(interaction)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self) -> None:
        """Tests the submit callback."""
        view = AdminConfigView()

        interaction = discord_mocks.InteractionMock(123456)
        values = [discord_mocks.MemberMock(123456 + x) for x in range(3)]
        interaction.data["values"] = values
        view.admins_select.refresh_state(interaction)

        with mock.patch("discord.ui.Select.values", new_callable=mock.PropertyMock, return_value=values):
            await view.submit_callback.callback(interaction)
