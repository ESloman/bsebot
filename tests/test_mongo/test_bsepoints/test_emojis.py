"""Tests our ServerEmojis class."""

import datetime
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.emojis import ServerEmojis
from mongo.datatypes.customs import EmojiDB
from tests.mocks import interface_mocks


class TestServerEmojis:
    """Tests our Guilds class."""

    def test_emojis_init(self) -> None:
        """Tests ServerEmojis init."""
        emojis = ServerEmojis()
        assert isinstance(emojis, ServerEmojis)

    def test_user_points_make_data_class(self) -> None:
        """Tests ServerEmojis make_data_class."""
        emojis = ServerEmojis()
        data = interface_mocks.query_mock("serveremojis", {})
        for entry in data:
            cls = emojis.make_data_class(entry)
            assert isinstance(cls, EmojiDB)

    @pytest.mark.parametrize(
        ("guild_id", "emoji_id"),
        # load list of entries dynamically
        sorted({(entry["guild_id"], entry["eid"]) for entry in interface_mocks.query_mock("serveremojis", {})}),
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_emojis_get_emoji(self, guild_id: int, emoji_id: int) -> None:
        """Tests ServerEmojis get_emoji method."""
        emojis = ServerEmojis()
        emoji = emojis.get_emoji(guild_id, emoji_id)
        assert isinstance(emoji, EmojiDB)
        assert emoji.guild_id == guild_id
        assert emoji.eid == emoji_id

    @pytest.mark.parametrize(
        ("guild_id", "name"),
        # load list of entries dynamically
        sorted({(entry["guild_id"], entry["name"]) for entry in interface_mocks.query_mock("serveremojis", {})}),
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_emojis_get_emoji_from_name(self, guild_id: int, name: str) -> None:
        """Tests ServerEmojis get_emoji_from_name method."""
        emojis = ServerEmojis()
        emoji = emojis.get_emoji_from_name(guild_id, name)
        assert isinstance(emoji, EmojiDB)
        assert emoji.guild_id == guild_id
        assert emoji.name == name

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_emojis_insert(self) -> None:
        """Tests ServerEmojis insert method."""
        emojis = ServerEmojis()
        with mock.patch.object(emojis, "insert") as updated_patch:
            emojis.insert_emoji(123456, "name", datetime.datetime.now(), 654321, 246810)
            assert updated_patch.called

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_emojis_get_emoji_none(self) -> None:
        """Tests ServerEmojis returns None correctly when getting."""
        emojis = ServerEmojis()
        emoji = emojis.get_emoji(123456, 654321)
        assert emoji is None

        emoji = emojis.get_emoji_from_name(123456, "some name")
        assert emoji is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        sorted({entry["guild_id"] for entry in interface_mocks.query_mock("serveremojis", {})}),
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_emojis_get_all_emojis(self, guild_id: int) -> None:
        """Tests ServerEmojis get_all_emojis method."""
        emojis = ServerEmojis()
        all_emojis = emojis.get_all_emojis(guild_id)
        for emoji in all_emojis:
            assert isinstance(emoji, EmojiDB)
            assert emoji.guild_id == guild_id
