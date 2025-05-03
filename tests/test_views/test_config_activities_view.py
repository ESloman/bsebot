"""Tests our Activity Config views."""

from unittest import mock

import pytest

from discordbot.views.config_activities import ActivityConfigView, ActivityConfirmView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


@pytest.mark.xfail
class TestActivityConfigView:
    """Tests our ActivityConfigView."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ActivityConfigView()

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = ActivityConfigView()
        interaction = discord_mocks.InteractionMock()
        await view.cancel_callback(None, interaction)

    async def test_update(self) -> None:
        """Tests update method."""
        view = ActivityConfigView()
        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = ["listening"]
        view.activity_select.refresh_state(interaction)
        await view.update(interaction)

    @pytest.mark.parametrize("activity_type", ["listening", "playing", "watching", "other"])
    async def test_submit_callback(self, activity_type: str) -> None:
        """Tests the submit callback."""
        view = ActivityConfigView()
        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = [activity_type]
        view.activity_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)


@pytest.mark.xfail
class TestActivityConfirmView:
    """Tests our ActivityConfirmView."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ActivityConfirmView("playing", "placeholder", ["something", "something"])

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = ActivityConfirmView("playing", "placeholder", ["something", "something"])
        interaction = discord_mocks.InteractionMock()
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("activity_type", ["listening", "playing", "watching"])
    @pytest.mark.parametrize(
        "names",
        [
            [
                "Stellaris",
            ],
            ["Stellaris", "something"],
            [
                "something",
            ],
            [
                "abc",
                "def",
            ],
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_submit_callback(self, activity_type: str, names: list[str]) -> None:
        """Tests the submit callback."""
        view = ActivityConfirmView(activity_type, "placeholder", names)
        interaction = discord_mocks.InteractionMock()
        await view.submit_callback.callback(interaction)
