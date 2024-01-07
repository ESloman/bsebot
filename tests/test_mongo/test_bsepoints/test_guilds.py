"""Tests our GuildDB class."""

from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes.guild import GuildDB
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
