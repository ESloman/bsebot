"""Tests our Daily Message views."""

from unittest import mock

import pytest

from discordbot.views.config_salary_message import DailyMessageView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestDailyMessageView:
    """Tests our DailyMessageView."""

    @pytest.mark.parametrize("enabled", [True, False])
    @pytest.mark.parametrize("admin", [True, False])
    @pytest.mark.parametrize("summary", [True, False])
    async def test_init(self, enabled: bool, admin: bool, summary: bool) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = DailyMessageView(enabled, admin, summary)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = DailyMessageView()
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("enabled", [True, False])
    @pytest.mark.parametrize("admin", [True, False])
    @pytest.mark.parametrize("summary", [True, False])
    @pytest.mark.parametrize("selected", ["enabled", "disabled"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, enabled: bool, admin: bool, summary: bool, selected: str) -> None:
        """Tests the submit callback."""
        view = DailyMessageView(enabled, admin, summary)

        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = [selected]

        view.enabled_select.refresh_state(interaction)
        if view.summary_select:
            view.summary_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)
