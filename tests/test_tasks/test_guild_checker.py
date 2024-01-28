"""Tests our guild checker task."""

from unittest import mock

import pytest

from discordbot.tasks.guildchecker import GuildChecker
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.datatypes.guild import GuildDB
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks, slashcommand_mocks


class TestActivityChanger:
    """Tests our ActivityChanger class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger
        self.close = slashcommand_mocks.CloseABetMock(self.bsebot, [], self.logger)
        self.place = slashcommand_mocks.PlaceABetMock(self.bsebot, [], self.logger)

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_create_new_guild(self, guild_data: dict) -> None:
        """Tests that we can create a new guild."""
        checker = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        guild_db = checker._create_new_guild(guild)
        assert isinstance(guild_db, GuildDB)
        assert guild_db.guild_id == guild_data["guild_id"]

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_check_guild_basic_info(self, guild_data: dict) -> None:
        """Tests that we can check the basic info of a guild.."""
        checker = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        guild_db = checker._check_guild_basic_info(guild)
        assert isinstance(guild_db, GuildDB)
        assert guild_db.guild_id == guild_data["guild_id"]

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_check_guild_basic_info_new_guild(self) -> None:
        """Tests that we can check the basic info of a guild with a new one."""
        checker = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(123456, 654321, "some name")
        guild_db = checker._check_guild_basic_info(guild)
        assert isinstance(guild_db, GuildDB)
        assert guild_db.guild_id == 123456

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_guild_members(self, guild_data: dict) -> None:
        """Tests that we can check the members of a guild."""
        checker = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_guild_members(guild)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_execution_default(self) -> None:
        """Tests default execution."""
        _ = GuildChecker(self.bsebot, [], self.logger, [], self.place, self.close, start=False)
