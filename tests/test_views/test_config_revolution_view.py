"""Tests our Revolution Config views."""

from unittest import mock

import pytest

from discordbot.views.config_revolution import RevolutionConfigView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestRevolutionConfigView:
    """Tests our RevolutionConfigView view."""

    @pytest.mark.parametrize("enabled", [True, False])
    async def test_init(self, enabled: bool) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = RevolutionConfigView(enabled)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = RevolutionConfigView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("value", ["enabled", "disabled"])
    @pytest.mark.parametrize("enabled", [True, False])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, value: str, enabled: bool) -> None:
        """Tests the submit callback."""
        view = RevolutionConfigView(enabled)

        interaction = discord_mocks.InteractionMock(123456)
        interaction.data["values"] = [value]
        view.enabled_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)
