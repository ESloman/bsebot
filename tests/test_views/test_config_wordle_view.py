"""Tests our Activity Config views."""

from unittest import mock

import pytest

from discordbot.views.config_wordle import (
    WordleConfigView,
    WordleEmojiReactionConfigView,
    WordleReminderConfirmView,
    WordleRootConfigView,
)
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestWordleRootConfigView:
    """Tests our WordleRootConfigView."""

    @pytest.mark.parametrize(
        "selectables", [[], ["wordle_config", "wordle_reactions", "wordle_reminders", "wordle_starting_words"]]
    )
    async def test_init(self, selectables: list[str]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = WordleRootConfigView(selectables)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = WordleRootConfigView()
        interaction = discord_mocks.InteractionMock()
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("option", [None, "something"])
    async def test_update(self, option: None | str) -> None:
        """Tests update method."""
        view = WordleRootConfigView()
        interaction = discord_mocks.InteractionMock()
        interaction.data["values"] = [option]
        view.wordle_config_select.refresh_state(interaction)
        await view.update(interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @pytest.mark.parametrize(
        "option", ["wordle_config", "wordle_reactions", "wordle_reminders", "wordle_starting_words", "other"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_submit_callback(self, guild_id: int, option: str) -> None:
        """Tests the submit callback."""
        view = WordleRootConfigView()
        interaction = discord_mocks.InteractionMock(guild_id)
        interaction.data["values"] = [option]
        view.wordle_config_select.refresh_state(interaction)

        with mock.patch.object(view.data_store, "get_starting_words", return_value={"words": ["adieu", "soare"]}):
            await view.submit_callback.callback(interaction)


class TestWordleConfigView:
    """Tests our WordleConfigView."""

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self, guild_id: int) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = WordleConfigView(guild_id)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_cancel_callback(self, guild_id: int) -> None:
        """Tests cancel callback."""
        view = WordleConfigView(guild_id)
        interaction = discord_mocks.InteractionMock(guild_id)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})[-1:]})
    @pytest.mark.parametrize("active", ["1", "0"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_update(self, guild_id: str, active: str) -> None:
        """Tests update method."""
        view = WordleConfigView(guild_id)
        interaction = discord_mocks.InteractionMock(guild_id)
        interaction.data["values"] = [active]
        view.active_select.refresh_state(interaction)
        await view.update(interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @pytest.mark.parametrize("active", ["1", "0"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, guild_id: int, active: str) -> None:
        """Tests the submit callback."""
        view = WordleConfigView(guild_id)

        interaction = discord_mocks.InteractionMock(guild_id)

        # set active
        interaction.data["values"] = [active]
        view.active_select.refresh_state(interaction)
        view.reminder_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)


class TestWordleEmojiReactionConfigView:
    """Tests our WordleEmojiReactionConfigView."""

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self, guild_id: int) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = WordleEmojiReactionConfigView(guild_id)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_cancel_callback(self, guild_id: int) -> None:
        """Tests cancel callback."""
        view = WordleEmojiReactionConfigView(guild_id)
        interaction = discord_mocks.InteractionMock(guild_id)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})[-1:]})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_update(self, guild_id: str) -> None:
        """Tests update method."""
        view = WordleEmojiReactionConfigView(guild_id)
        interaction = discord_mocks.InteractionMock(guild_id)
        await view.update(interaction)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_submit_callback(self, guild_id: int) -> None:
        """Tests the submit callback."""
        view = WordleEmojiReactionConfigView(guild_id)
        interaction = discord_mocks.InteractionMock(guild_id)

        # set active
        interaction.data["values"] = [":one:"]
        view.x_select.refresh_state(interaction)
        view.two_select.refresh_state(interaction)
        view.six_select.refresh_state(interaction)

        await view.submit_callback.callback(interaction)


class TestWordleReminderConfirmView:
    """Tests our WordleReminderConfirmView."""

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = WordleReminderConfirmView("some name")

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = WordleReminderConfirmView("some name")
        interaction = discord_mocks.InteractionMock()
        await view.cancel_callback(None, interaction)

    async def test_edit_callback(self) -> None:
        """Tests edit callback."""
        view = WordleReminderConfirmView("some name")
        interaction = discord_mocks.InteractionMock()
        await view.edit_callback.callback(interaction)

    @pytest.mark.parametrize(
        "name", ["some name", interface_mocks.query_mock("wordlereminders", {"archived": False})[-1]["name"]]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_submit_callback(self, name: str) -> None:
        """Tests the submit callback."""
        view = WordleReminderConfirmView(name)

        interaction = discord_mocks.InteractionMock()

        await view.submit_callback.callback(interaction)
