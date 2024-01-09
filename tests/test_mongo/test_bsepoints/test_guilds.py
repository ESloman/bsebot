"""Tests our GuildDB class."""

import datetime
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.user import UserDB
from tests.mocks import interface_mocks


class TestGuilds:
    """Tests our Guilds class."""

    def test_guilds_init(self) -> None:  # noqa: PLR6301
        """Tests Guilds init."""
        guilds = Guilds()
        assert isinstance(guilds, Guilds)
        assert guilds.database is not None
        assert guilds.vault is not None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_guild(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds get_guild method."""
        guilds = Guilds()
        guild = guilds.get_guild(guild_id)
        assert isinstance(guild, GuildDB)
        assert guild.guild_id == guild_id

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_guild_none(self) -> None:  # noqa: PLR6301
        """Tests Guilds get_guild method."""
        guilds = Guilds()
        guild = guilds.get_guild(123456)
        assert guild is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_guilds_insert_guild(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds insert_guild method."""
        guilds = Guilds()
        guilds.insert_guild(guild_id, "name", 123456, datetime.datetime.now())

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_channel(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds get_channel method."""
        guilds = Guilds()
        channel = guilds.get_channel(guild_id)
        assert channel is not None
        assert isinstance(channel, int)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_channel_none(self) -> None:  # noqa: PLR6301
        """Tests Guilds get_channel method return None as expected."""
        guilds = Guilds()
        channel = guilds.get_channel(123456)
        assert channel is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds get_king method."""
        guilds = Guilds()
        king = guilds.get_king(guild_id)
        assert king is not None
        assert isinstance(king, int)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king_whole_class(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds get_king method and return the whole class."""
        guilds = Guilds()
        king = guilds.get_king(guild_id, True)
        assert king is not None
        assert isinstance(king, UserDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king_none(self) -> None:  # noqa: PLR6301
        """Tests Guilds get_king method return None as expected."""
        guilds = Guilds()
        king = guilds.get_king(123456)
        assert king is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_king(self, guild_id: int) -> None:  # noqa: PLR6301
        """Tests Guilds set_king method."""
        guilds = Guilds()
        with mock.patch.object(guilds, "update") as update_patched:
            guilds.set_king(guild_id, 123456)
            assert update_patched.called
            assert len(update_patched.call_args) == 2
