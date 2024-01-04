"""Tests our highscore related functions in Embed Manager."""

from unittest.mock import patch

from discordbot.embedmanager import EmbedManager
from tests.mocks import mongo_mocks
from tests.mocks.discord_mocks import GuildMock


class TestHighscoreEmbed:
    @staticmethod
    def test_get_highscore_embed() -> None:
        """Tests our get_highscore_embed with some standard parameters."""
        guild = GuildMock(123456)

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock()):
            embed = embeds.get_highscore_embed(guild, None, "someone")
        assert isinstance(embed, str)

    @staticmethod
    def test_get_highscore_embed_with_number() -> None:
        """Tests our get_highscore_embed with some standard parameters."""
        guild = GuildMock(123456)

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock()):
            embed = embeds.get_highscore_embed(guild, 5, "someone")
        assert isinstance(embed, str)
