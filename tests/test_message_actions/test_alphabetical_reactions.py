"""Tests our WordleReactions message action class."""

from unittest import mock

import pytest

from discordbot.message_actions.alphabetical_reactions import AlphabeticalMessageAction
from discordbot.message_actions.base import BaseMessageAction
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestWordleReactions:
    """Tests our WordleReactions class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests init."""
        action = AlphabeticalMessageAction(self.client, self.logger)
        assert isinstance(action, BaseMessageAction)

    @pytest.mark.parametrize("content", ["", "a short text", "a b c", "a longer message not mangled"])
    async def test_pre_condition_fail(self, content: str) -> None:
        """Tests the pre_condition function evalutates to False correctly."""
        action = AlphabeticalMessageAction(self.client, self.logger)
        assert not await action.pre_condition(discord_mocks.MessageMock(content), ["message"])

    @pytest.mark.parametrize(
        "content",
        [
            "a basic message someone",
            "something something something thanks",
            "The underwear was zany.",
            "A basic cat drank everything.",
            "Who? You? Zap zip.",
            "Now that's wank. Zippity zoo.",
        ],
    )
    async def test_pre_condition_pass(self, content: str) -> None:
        """Tests the pre_condition function evalutates to False correctly."""
        action = AlphabeticalMessageAction(self.client, self.logger)
        assert await action.pre_condition(discord_mocks.MessageMock(content), ["message"])

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_run(self) -> None:
        """Tests the run function."""
        action = AlphabeticalMessageAction(self.client, self.logger)
        await action.run(discord_mocks.MessageMock())
