"""Tests our guild checker task."""

import operator
from unittest import mock

import pytest

from discordbot.tasks.guildchecker import GuildChecker
from mongo import interface
from mongo.datatypes.guild import GuildDB
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks, slashcommand_mocks


@pytest.mark.xfail
class TestGuildChecker:
    """Tests our GuildChecker class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.close = slashcommand_mocks.CloseABetMock(self.bsebot, [])
        self.place = slashcommand_mocks.PlaceABetMock(self.bsebot, [])

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = GuildChecker(self.bsebot, [], self.place, self.close, start=False)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_create_new_guild(self, guild_data: dict) -> None:
        """Tests that we can create a new guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        guild_db = checker._create_new_guild(guild)
        assert isinstance(guild_db, GuildDB)
        assert guild_db.guild_id == guild_data["guild_id"]

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_check_guild_basic_info(self, guild_data: dict) -> None:
        """Tests that we can check the basic info of a guild.."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
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
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(123456, 654321, "some name")
        guild_db = checker._check_guild_basic_info(guild)
        assert isinstance(guild_db, GuildDB)
        assert guild_db.guild_id == 123456

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_guild_members(self, guild_data: dict) -> None:
        """Tests that we can check the members of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_guild_members(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_guild_emojis(self, guild_data: dict) -> None:
        """Tests that we can check the emojis of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_guild_emojis(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_guild_stickers(self, guild_data: dict) -> None:
        """Tests that we can check the emojis of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_guild_stickers(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_guild_join_threads(self, guild_data: dict) -> None:
        """Tests that we can check the threads of a guild and join them."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_guild_join_threads(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_threads(self, guild_data: dict) -> None:
        """Tests that we can check the threads of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_threads(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_events(self, guild_data: dict) -> None:
        """Tests that we can check the events of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        checker._check_events(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_bets(self, guild_data: dict) -> None:
        """Tests that we can check the bets of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_bets(guild)

    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=operator.itemgetter("guild_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_check_channels(self, guild_data: dict) -> None:
        """Tests that we can check the channels of a guild."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        await checker._check_channels(guild)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_execution_default(self) -> None:
        """Tests default execution."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        await checker.guild_checker()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_execution_finished(self) -> None:
        """Tests default execution when we've already set finished."""
        checker = GuildChecker(self.bsebot, [], self.place, self.close, start=False)
        checker.finished = True
        await checker.guild_checker()
