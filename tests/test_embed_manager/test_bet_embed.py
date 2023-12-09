"""Tests our bet related functions in Embed Manager."""

from unittest.mock import patch

import discord

from discordbot.embedmanager import EmbedManager
from tests.mocks import embed_mocks, mongo_mocks
from tests.mocks.discord_mocks import GuildMock


class TestBetEmbed:
    @staticmethod
    def test_get_bet_embed() -> None:
        """Tests our get_bet_embed with some standard parameters."""
        bet = embed_mocks.get_bet()
        guild = GuildMock()

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_embed_empty() -> None:
        """Tests our get_bet_embed with no betters."""
        bet = embed_mocks.get_bet()
        bet["option_dict"] = {}
        guild = GuildMock()

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_not_active() -> None:
        """Tests our get_bet_embed with an inactive bet."""
        bet = embed_mocks.get_bet()
        bet["active"] = False
        guild = GuildMock()

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_embed_with_empty_id() -> None:
        """Tests our get_bet_embed with an empty id."""
        bet = embed_mocks.get_bet()
        bet["betters"]["0"] = {"user_id": 0, "emoji": "1", "points": 10}
        guild = GuildMock()

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock):
            embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)
