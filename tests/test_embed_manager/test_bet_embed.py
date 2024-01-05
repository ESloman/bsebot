"""Tests our bet related functions in Embed Manager."""

import copy
import dataclasses
from unittest.mock import patch

import discord

from discordbot.embedmanager import EmbedManager
from mongo.datatypes import Better
from tests.mocks import embed_mocks, mongo_mocks
from tests.mocks.discord_mocks import GuildMock


class TestBetEmbed:
    @staticmethod
    def test_get_bet_embed() -> None:
        """Tests our get_bet_embed with some standard parameters."""
        bet = embed_mocks.get_bet()
        guild = GuildMock(123456)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_embed_empty() -> None:
        """Tests our get_bet_embed with no betters."""
        bet = embed_mocks.get_bet()
        dataclasses.replace(bet, option_dict={})
        guild = GuildMock(123456)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_not_active() -> None:
        """Tests our get_bet_embed with an inactive bet."""
        bet = embed_mocks.get_bet()
        bet = dataclasses.replace(bet, active=False)
        guild = GuildMock(123456)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)

    @staticmethod
    def test_get_bet_embed_with_empty_id() -> None:
        """Tests our get_bet_embed with an empty id."""
        bet = embed_mocks.get_bet()
        new_betters = copy.deepcopy(bet.betters)
        new_betters["0"] = Better(user_id=0, emoji="1", points=10)
        bet = dataclasses.replace(bet, betters=new_betters)
        guild = GuildMock(123456)

        embeds = EmbedManager()
        with patch.object(embeds, "user_points", new=mongo_mocks.UserPointsMock()):
            embed = embeds.get_bet_embed(guild, bet)
        assert isinstance(embed, discord.Embed)
