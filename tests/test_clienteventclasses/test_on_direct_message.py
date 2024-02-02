"""Tests our OnDirectMessage client event class."""

import pytest

from apis.giphyapi import GiphyAPI
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.ondirectmessage import OnDirectMessage
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnDirectMessage:
    """Tests our OnDirectMessage commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger
        self.giphy = GiphyAPI("")

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnDirectMessage(self.client, [], self.logger, self.giphy)
        assert isinstance(event, OnDirectMessage)
        assert isinstance(event, BaseEvent)
