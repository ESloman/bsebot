"""Tests our CommandSuggest message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.command_suggestion import CommandSuggest
from tests.mocks.bsebot_mocks import BSEBotMock


class TestCommandSuggest:
    """Tests our CommandSuggest class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests init."""
        action = CommandSuggest(self.client)
        assert isinstance(action, BaseMessageAction)
