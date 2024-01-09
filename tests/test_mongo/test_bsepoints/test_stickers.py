"""Tests our ServerStickers class."""

import datetime
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.stickers import ServerStickers
from mongo.datatypes.customs import StickerDB
from tests.mocks import interface_mocks


class TestServerStickers:
    """Tests our Guilds class."""

    def test_stickers_init(self) -> None:
        """Tests ServerStickers init."""
        stickers = ServerStickers()
        assert isinstance(stickers, ServerStickers)

    def test_user_points_make_data_class(self) -> None:
        """Tests ServerStickers make_data_class."""
        stickers = ServerStickers()
        data = interface_mocks.query_mock("serverstickers", {})
        for entry in data:
            cls = stickers.make_data_class(entry)
            assert isinstance(cls, StickerDB)

    @pytest.mark.parametrize(
        ("guild_id", "sticker_id"),
        # load list of entries dynamically
        {(entry["guild_id"], entry["stid"]) for entry in interface_mocks.query_mock("serverstickers", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stickers_get_sticker(self, guild_id: int, sticker_id: int) -> None:
        """Tests ServerStickers get_sticker method."""
        stickers = ServerStickers()
        sticker = stickers.get_sticker(guild_id, sticker_id)
        assert isinstance(sticker, StickerDB)
        assert sticker.guild_id == guild_id
        assert sticker.stid == sticker_id

    @pytest.mark.parametrize(
        ("guild_id", "name"),
        # load list of entries dynamically
        {(entry["guild_id"], entry["name"]) for entry in interface_mocks.query_mock("serverstickers", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stickers_get_sticker_from_name(self, guild_id: int, name: str) -> None:
        """Tests ServerStickers get_sticker_from_name method."""
        stickers = ServerStickers()
        sticker = stickers.get_sticker_from_name(guild_id, name)
        assert isinstance(sticker, StickerDB)
        assert sticker.guild_id == guild_id
        assert sticker.name == name

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_stickers_insert(self) -> None:
        """Tests ServerStickers insert method."""
        stickers = ServerStickers()
        with mock.patch.object(stickers, "insert") as updated_patch:
            stickers.insert_sticker(123456, "name", datetime.datetime.now(), 654321, 246810)
            assert updated_patch.called
