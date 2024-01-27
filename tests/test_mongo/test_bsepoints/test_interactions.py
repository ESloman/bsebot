"""Tests our UserInteractions class."""

import datetime
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.interactions import UserInteractions
from mongo.datatypes.message import MessageDB, ReactionDB, ReplyDB, VCInteractionDB
from tests.mocks import interface_mocks

INTERACTION_CACHE: list[dict[str, any]] | None = None


def _get_interaction_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global INTERACTION_CACHE  # noqa: PLW0603
    if INTERACTION_CACHE is None:
        INTERACTION_CACHE = list(interface_mocks.query_mock("userinteractions", {}))
    if not number:
        return INTERACTION_CACHE
    return INTERACTION_CACHE[-number:]


class TestUserInteractions:
    """Tests our UserInteractions class."""

    def test_user_interactions_init(self) -> None:
        """Tests UserInteractions init."""
        user_interactions = UserInteractions()
        assert isinstance(user_interactions, UserInteractions)

    def test_interactions_make_data_class(self) -> None:
        """Tests UserInteractions make_data_class."""
        user_interactions = UserInteractions()
        data = _get_interaction_data()
        for entry in data:
            cls = user_interactions.make_data_class(entry)
            assert isinstance(cls, MessageDB | VCInteractionDB)
            if isinstance(cls, MessageDB):
                new_cls = user_interactions.make_data_class(cls)
                # should be no change
                assert new_cls is cls

    @pytest.mark.parametrize(
        "guild_id", sorted({entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})})
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_interactions_get_messages_for_server(self, guild_id: int) -> None:
        """Tests UserInteractions get_messages_for_server method."""
        user_interactions = UserInteractions()
        messages = user_interactions.get_all_messages_for_server(guild_id)
        assert isinstance(messages, list)
        for message in messages:
            assert isinstance(message, MessageDB | VCInteractionDB)

    @pytest.mark.parametrize(
        ("guild_id", "channel_id"),
        sorted({(entry["guild_id"], entry["channel_id"]) for entry in _get_interaction_data()})[:5],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_interactions_get_messages_for_channel(self, guild_id: int, channel_id: int) -> None:
        """Tests UserInteractions get_messages_for_server method."""
        user_interactions = UserInteractions()
        messages = user_interactions.get_all_messages_for_channel(guild_id, channel_id)
        assert isinstance(messages, list)
        for message in messages:
            assert isinstance(message, MessageDB | VCInteractionDB)

    @pytest.mark.parametrize(
        ("guild_id", "message_id"),
        [
            *sorted({(entry["guild_id"], entry.get("message_id", 123456)) for entry in _get_interaction_data(20)}),
            (123456, 654321),
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_interactions_get_message(self, guild_id: int, message_id: int) -> None:
        """Tests UserInteractions get_message method."""
        user_interactions = UserInteractions()
        message = user_interactions.get_message(guild_id, message_id)
        assert isinstance(message, MessageDB | VCInteractionDB | None)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_interactions_add_entry(self) -> None:
        """Tests UserInteractions add_entry method."""
        user_interactions = UserInteractions()
        entry = {
            "message_id": 123456,
            "guild_id": 654321,
            "channel_id": 321456,
            "user_id": 456321,
            "message_type": ["message", "link"],
            "message_content": "some message content",
            "timestamp": datetime.datetime.now(),
            "is_bot": False,
        }
        inserted = user_interactions.add_entry(**entry)
        assert isinstance(inserted, MessageDB)

        other_entry = {
            "message_id": 123456,
            "guild_id": 654321,
            "channel_id": 321456,
            "user_id": 456321,
            "message_type": ["message", "link"],
            "message_content": "some message content",
            "timestamp": datetime.datetime.now(),
            "is_bot": False,
            "additional_keys": {"og_mid": 987654},
        }
        inserted = user_interactions.add_entry(**other_entry)
        assert isinstance(inserted, MessageDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_user_interactions_add_voice_entry(self) -> None:
        """Tests UserInteractions add_voice_entry method."""
        user_interactions = UserInteractions()
        entry = {
            "guild_id": 654321,
            "channel_id": 321456,
            "user_id": 456321,
            "timestamp": datetime.datetime.now(),
            "muted": False,
            "deafened": False,
            "streaming": False,
        }
        inserted = user_interactions.add_voice_state_entry(**entry)
        assert isinstance(inserted, VCInteractionDB)

    @pytest.mark.parametrize("entry", [entry for entry in _get_interaction_data() if entry.get("active")])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_user_interactions_find_active_voice_state(self, entry: dict[str, any]) -> None:
        """Tests UserInteractions find_active_voice_state method."""
        user_interactions = UserInteractions()
        # should find None
        state = user_interactions.find_active_voice_state(123456, 654321, 123654, datetime.datetime.now())
        assert state is None

        state = user_interactions.find_active_voice_state(
            entry["guild_id"], entry["user_id"], entry["channel_id"], datetime.datetime.now()
        )
        assert isinstance(state, VCInteractionDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_interactions_add_reply_to_message(self) -> None:
        """Tests UserInteractions add_reply_to_message method."""
        user_interactions = UserInteractions()
        reply = user_interactions.add_reply_to_message(
            123456, 654321, 123654, 654123, datetime.datetime.now(), "content"
        )
        assert isinstance(reply, ReplyDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_interactions_add_reaction_to_message(self) -> None:
        """Tests UserInteractions add_reaction_to_message method."""
        user_interactions = UserInteractions()
        reply = user_interactions.add_reaction_entry(
            123456,
            654321,
            123654,
            654123,
            datetime.datetime.now(),
            ":rey:",
            987654,
        )
        assert isinstance(reply, ReactionDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_user_interactions_remove_reaction_to_message(self) -> None:
        """Tests UserInteractions remove_reaction_to_message method."""
        user_interactions = UserInteractions()
        user_interactions.remove_reaction_entry(
            123456,
            654321,
            123654,
            654123,
            datetime.datetime.now(),
            ":rey:",
            987654,
        )
