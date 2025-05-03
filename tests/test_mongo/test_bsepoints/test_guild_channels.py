"""Tests our GuildChannels class."""

import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from bson import ObjectId

from mongo import interface
from mongo.bsepoints.channels import GuildChannels
from tests.mocks import interface_mocks


@pytest.mark.xfail
class TestGuildChannels:
    """Tests our GuildChannels class."""

    def test_guild_channels_init(self) -> None:
        """Tests GuildChannels init."""
        guild_channels = GuildChannels()
        assert isinstance(guild_channels, GuildChannels)
        assert guild_channels.database is not None
        assert guild_channels.vault is not None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_guild_channels_insert(self) -> None:
        """Tests GuildChannels insert."""
        guild_channels = GuildChannels()
        guild_channels.insert_channel(
            123456, 654321, 5, "some-channel-name", datetime.datetime.now(tz=ZoneInfo("UTC")), 654789, False
        )

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guild_channels_find_empty(self) -> None:
        """Tests GuildChannels find with a bad channel."""
        guild_channels = GuildChannels()
        channel_db = guild_channels.find_channel(123456, 654321)
        assert channel_db is None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guild_channels_update(self) -> None:
        """Tests GuildChannels update."""
        guild_channels = GuildChannels()
        channel_db = guild_channels.make_data_class({
            "_id": ObjectId(),
            "guild_id": 123456789,
            "channel_id": 987654321,
            "name": "some-channel-name",
            "type": 5,
            "created": datetime.datetime.now(tz=ZoneInfo("UTC")),
            "category_id": 123654789,
            "is_nsfw": False,
        })
        new_channel_db = guild_channels.update_channel(channel_db, "some-other-name", True)
        assert channel_db != new_channel_db
        assert channel_db.name != new_channel_db.name
        assert channel_db.is_nsfw != new_channel_db.is_nsfw
