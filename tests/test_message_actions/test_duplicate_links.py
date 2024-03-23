"""Tests our DuplicateLinkAction message action class."""

from unittest import mock

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.duplicate_links import DuplicateLinkAction
from mongo import interface
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestDuplicateLinkAction:
    """Tests our DuplicateLinkAction class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests init."""
        action = DuplicateLinkAction(self.client)
        assert isinstance(action, BaseMessageAction)

    @pytest.mark.parametrize("entry", interface_mocks.query_mock("userinteractions", {"message_type": "message"})[-50:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_pre_condition(self, entry: dict[str, any]) -> None:
        """Tests precondition with various bits of data."""
        action = DuplicateLinkAction(self.client)
        message = discord_mocks.MessageMock(entry["content"], entry["guild_id"], entry["message_id"])
        success = await action.pre_condition(message, entry["message_type"])
        assert isinstance(success, bool)

    @pytest.mark.parametrize("entry", interface_mocks.query_mock("userinteractions", {"message_type": "link"})[-10:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_run(self, entry: dict[str, any]) -> None:
        """Tests run with various bits of data."""
        action = DuplicateLinkAction(self.client)
        message = discord_mocks.MessageMock(entry["content"], entry["guild_id"], entry["message_id"])
        action._results_map[message.id] = [discord_mocks.MessageMock(entry["content"], entry["guild_id"], 123456)]
        await action.run(message)
