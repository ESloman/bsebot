"""Tests our Salary Config views."""

from unittest import mock

import pytest

from discordbot.views.config_threads import ThreadConfigView
from mongo import interface
from mongo.bsedataclasses import SpoilerThreads
from tests.mocks import discord_mocks, interface_mocks


@pytest.mark.xfail
class TestThreadConfigView:
    """Tests our ThreadConfigView view."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        threads = [
            SpoilerThreads.make_data_class(thread) for thread in interface_mocks.query_mock("spoilerthreads", {})[-10:]
        ]
        _ = ThreadConfigView(threads)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        threads = [
            SpoilerThreads.make_data_class(thread) for thread in interface_mocks.query_mock("spoilerthreads", {})[-10:]
        ]
        view = ThreadConfigView(threads)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize(
        "thread_id",
        [str(thread["thread_id"]) for thread in interface_mocks.query_mock("spoilerthreads", {"active": True})[-10:]],
    )
    async def test_update(self, thread_id: str) -> None:
        """Tests update method."""
        threads = [
            SpoilerThreads.make_data_class(thread)
            for thread in interface_mocks.query_mock("spoilerthreads", {"active": True})[-10:]
        ]
        view = ThreadConfigView(threads)
        interaction = discord_mocks.InteractionMock(123456)
        interaction.data["values"] = [thread_id]
        view.thread_select.refresh_state(interaction)

        await view.update(interaction)

    @pytest.mark.parametrize(
        "thread_id",
        [str(thread["thread_id"]) for thread in interface_mocks.query_mock("spoilerthreads", {"active": True})[-1:]],
    )
    @pytest.mark.parametrize("day", list(range(8)))
    @pytest.mark.parametrize("active", ["0", "1"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, thread_id: str, day: int, active: str) -> None:
        """Tests the submit callback."""
        threads = [
            SpoilerThreads.make_data_class(thread)
            for thread in interface_mocks.query_mock("spoilerthreads", {"active": True})[-10:]
        ]
        view = ThreadConfigView(threads)

        interaction = discord_mocks.InteractionMock()

        # update thread select
        interaction.data["values"] = [thread_id]
        view.thread_select.refresh_state(interaction)

        # update day select
        interaction.data["values"] = [str(day)]
        view.day_select.refresh_state(interaction)

        # update active select
        interaction.data["values"] = [active]
        view.active_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)
