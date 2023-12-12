"""Tests the BSEBot class."""

from unittest.mock import patch

import discord
import pytest

from discordbot.bsebot import BSEBot
from tests.mocks import bsebot_mocks


class TestBSEBot:
    """Tests our BSEBot class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Test data."""
        self.intents = discord.Intents.all()
        self.activity = discord.Activity(
            name="conversations",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )

    def test_init(self) -> None:
        """Tests that we can initialise the class."""
        bsebot = BSEBot(self.intents, self.activity)
        assert isinstance(bsebot, discord.Bot)

    @patch.object(discord.Bot, "get_guild", new=bsebot_mocks.get_guild)
    async def test_fetch_guild_get(self) -> None:
        """Tests getting a guild when it's already in the cache."""
        bsebot = BSEBot(self.intents, self.activity)
        guild = await bsebot.fetch_guild(123)
        assert guild.id == 123

    @patch.object(discord.Bot, "get_guild", new=bsebot_mocks.get_guild)
    @patch.object(discord.Bot, "fetch_guild", new=bsebot_mocks.fetch_guild)
    async def test_fetch_guild_fetch(self) -> None:
        """Tests getting a guild when it's not in the cache."""
        bsebot = BSEBot(self.intents, self.activity)
        guild = await bsebot.fetch_guild(456)
        assert guild.id == 456

    @patch.object(discord.Bot, "get_channel", new=bsebot_mocks.get_channel)
    async def test_fetch_channel_get(self) -> None:
        """Tests getting a channel when it's already in the cache."""
        bsebot = BSEBot(self.intents, self.activity)
        channel = await bsebot.fetch_channel(123456)
        assert channel.id == 123456

    @patch.object(discord.Bot, "get_channel", new=bsebot_mocks.get_channel)
    @patch.object(discord.Bot, "fetch_channel", new=bsebot_mocks.fetch_channel)
    async def test_fetch_channel_fetch(self) -> None:
        """Tests getting a channel when it's not in the cache."""
        bsebot = BSEBot(self.intents, self.activity)
        channel = await bsebot.fetch_channel(654321)
        assert channel.id == 654321
