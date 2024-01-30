"""Tests our Active Slash Command class."""

from unittest import mock

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestClose:
    """Tests our Close commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()
        self.guild_ids = [123456, 65321]
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        close = CloseBet(self.client, self.guild_ids, self.logger)
        assert isinstance(close, CloseBet)
        assert isinstance(close, BSEddies)
        assert isinstance(close, BaseEvent)
        assert close.activity_type == ActivityTypes.BSEDDIES_BET_CLOSE
        assert close.help_string is not None

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_create_bet_view(self, guild_data: dict) -> None:
        """Tests create_bet_view with no bets."""
        close = CloseBet(self.client, self.guild_ids, self.logger)

        guild = Guilds.make_data_class(guild_data)
        _users = interface_mocks.query_mock("userpoints", {"guild_id": guild.guild_id})
        for user in _users:
            _bets = interface_mocks.query_mock("userbets", {"guild_id": guild.guild_id, "user_id": user["uid"]})
            if _bets:
                break
        ctx = discord_mocks.ContextMock(guild.guild_id, user["uid"])
        await close.create_bet_view(ctx)
