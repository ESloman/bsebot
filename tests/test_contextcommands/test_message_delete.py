"""Tests our ContextDeleteMessage context command class."""

import pytest

from discordbot.contextcommands.base import BaseContextCommand
from discordbot.contextcommands.message_delete import ContextDeleteMessage
from tests.mocks.bsebot_mocks import BSEBotMock


class TestContextDeleteMessage:
    """Tests our ContextDeleteMessage class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests init."""
        command = ContextDeleteMessage(self.client)
        assert isinstance(command, BaseContextCommand)
