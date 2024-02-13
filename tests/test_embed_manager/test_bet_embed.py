"""Tests our bet related functions in Embed Manager."""

import copy
import dataclasses
from unittest import mock

import discord
import pytest

from discordbot.embedmanager import EmbedManager
from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetterDB
from tests.mocks import interface_mocks


class TestBetEmbed:
    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-10:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_get_bet_embed(self, bet_data: dict[str, any]) -> None:
        """Tests our get_bet_embed with some standard parameters."""
        bet = UserBets.make_data_class(bet_data)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(bet)
        assert isinstance(embed, discord.Embed)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-2:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_get_bet_embed_empty(self, bet_data: dict[str, any]) -> None:
        """Tests our get_bet_embed with no betters."""
        bet = UserBets.make_data_class(bet_data)
        dataclasses.replace(bet, option_dict={})

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(bet)
        assert isinstance(embed, discord.Embed)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-2:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_get_bet_not_active(self, bet_data: dict[str, any]) -> None:
        """Tests our get_bet_embed with an inactive bet."""
        bet = UserBets.make_data_class(bet_data)
        bet = dataclasses.replace(bet, active=False)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(bet)
        assert isinstance(embed, discord.Embed)

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-1:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_get_bet_embed_with_empty_id(self, bet_data: dict[str, any]) -> None:
        """Tests our get_bet_embed with an empty id."""
        bet = UserBets.make_data_class(bet_data)
        new_betters = copy.deepcopy(bet.betters)
        new_betters["0"] = BetterDB(user_id=0, emoji="1", points=10)
        bet = dataclasses.replace(bet, betters=new_betters)

        embeds = EmbedManager()
        embed = embeds.get_bet_embed(bet)
        assert isinstance(embed, discord.Embed)
