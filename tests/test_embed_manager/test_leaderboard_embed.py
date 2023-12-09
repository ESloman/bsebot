"""Tests our leaderboard related functions in Embed Manager."""

from unittest.mock import patch

from discordbot.embedmanager import EmbedManager
from tests.mocks import mongo_mocks
from tests.mocks.discord_mocks import GuildMock


class TestLeaderboardEmbed:
    @staticmethod
    def test_get_leaderboard_embed() -> None:
        """Tests our get_leaderboard_embed with some standard parameters."""
        guild = GuildMock()

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock()):
            embed = embeds.get_leaderboard_embed(guild, None, "someone")
        assert isinstance(embed, str)

    @staticmethod
    def test_get_leaderboard_embed_with_number() -> None:
        """Tests our get_leaderboard_embed with some standard parameters."""
        guild = GuildMock()

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock()):
            embed = embeds.get_leaderboard_embed(guild, 5, "someone")
        assert isinstance(embed, str)
