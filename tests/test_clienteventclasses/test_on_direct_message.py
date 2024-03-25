"""Tests our OnDirectMessage client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.ondirectmessage import OnDirectMessage
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnDirectMessage:
    """Tests our OnDirectMessage commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnDirectMessage(self.client)
        assert isinstance(event, OnDirectMessage)
        assert isinstance(event, BaseEvent)
