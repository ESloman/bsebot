"""Tests our revolution related functions in Embed Manager."""

from discordbot.embedmanager import EmbedManager
from tests.mocks import embed_mocks
from tests.mocks.discord_mocks import GuildMock, MemberMock, RoleMock


class TestRevolutionEmbed:
    @staticmethod
    def test_get_revolution_message() -> None:
        """Tests our get_revolution_message with some standard parameters."""
        guild = GuildMock()
        king = MemberMock(123456, "king_name", "king_mention")
        role = RoleMock(123456, "revolution", "revolution")
        event = embed_mocks.get_event()

        embeds = EmbedManager()
        embed = embeds.get_revolution_message(king, role, event, guild)
        assert isinstance(embed, str)
