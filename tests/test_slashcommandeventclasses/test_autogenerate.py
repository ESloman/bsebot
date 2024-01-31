"""Tests our Active Slash Command class."""

from unittest import mock

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.autogenerate import AutoGenerate
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.guilds import Guilds
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestAutoGenerate:
    """Tests our AutoGenerate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()
        self.guild_ids = [123456, 65321]
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        autogenerate = AutoGenerate(self.client, self.guild_ids, self.logger)
        assert isinstance(autogenerate, AutoGenerate)
        assert isinstance(autogenerate, BSEddies)
        assert isinstance(autogenerate, BaseEvent)
        assert autogenerate.activity_type == ActivityTypes.BSEDDIES_AUTOGENERATE
        assert autogenerate.help_string is not None

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_create_auto_generate_view(self, guild_data: dict) -> None:
        """Tests create_auto_generate_view."""
        close = AutoGenerate(self.client, self.guild_ids, self.logger)

        guild = Guilds.make_data_class(guild_data)
        ctx = discord_mocks.ContextMock(guild.guild_id, guild.king)
        await close.create_auto_generate_view(ctx)
