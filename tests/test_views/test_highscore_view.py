"""Tests our highscore view."""

from unittest import mock

import pytest

from discordbot.embedmanager import EmbedManager
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.highscore import HighScoreBoardView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestHighscoreView:
    """Tests our Highscore view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.embed_manager = EmbedManager(PlaceHolderLogger)

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = HighScoreBoardView(self.embed_manager)

    @pytest.mark.parametrize("guild_id", {guild["guild_id"] for guild in interface_mocks.query_mock("guilds", {})})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_button_callback(self, guild_id: int) -> None:
        """Tests button callback."""
        view = HighScoreBoardView(self.embed_manager)
        interaction = discord_mocks.InteractionMock(guild_id)
        await view.button_callback.callback(interaction)
