"""Tests our revolution related functions in Embed Manager."""

import dataclasses
import re
from unittest.mock import patch

import pytest

from discordbot.embedmanager import EmbedManager
from tests.mocks import embed_mocks
from tests.mocks.discord_mocks import GuildMock, MemberMock, RoleMock


class TestRevolutionEmbed:
    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        self.guild = GuildMock(123456)
        self.king = MemberMock(123456, "king_name", "king_mention")
        self.role = RoleMock(123456, "revolution", "revolution")
        self.event = embed_mocks.get_event()

    def test_get_revolution_message(self) -> None:
        """Tests our get_revolution_message with some standard parameters."""
        embeds = EmbedManager()
        embed = embeds.get_revolution_message(self.king, self.role, self.event, self.guild)
        assert isinstance(embed, str)

    @pytest.mark.parametrize("chance", [0, 15, 30, 60, -100, 115])
    def test_get_revolution_message_different_chances(self, chance: int) -> None:
        """Tests our get_revolution_message with different chances."""
        event = dataclasses.replace(self.event, chance=chance)
        embeds = EmbedManager()
        embed = embeds.get_revolution_message(self.king, self.role, event, self.guild)
        assert isinstance(embed, str)

        # make sure that chance is within 5% -> 95%
        match = re.search(r"`-?\d+%`", embed)
        assert match is not None
        chance_num = int(match.group().strip("`").strip("%"))
        assert 5 <= chance_num <= 95

    def test_get_revolution_message_no_member(self) -> None:
        """Tests our get_revolution_message with get_member returning None."""
        embeds = EmbedManager()
        with patch.object(self.guild, "get_member", new=lambda _: None):
            embed = embeds.get_revolution_message(self.king, self.role, self.event, self.guild)
        assert isinstance(embed, str)

    def test_get_revolution_message_no_users(self) -> None:
        """Tests our get_revolution_message with empty participants."""
        event = dataclasses.replace(self.event, revolutionaries=[], supporters=[])

        embeds = EmbedManager()
        embed = embeds.get_revolution_message(self.king, self.role, event, self.guild)
        assert isinstance(embed, str)
