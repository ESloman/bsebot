"""Tests our OnReadyEvent client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onready import OnReadyEvent
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnReadyEvent:
    """Tests our OnReadyEvent commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnReadyEvent(self.client, [], self.logger)
        assert isinstance(event, OnReadyEvent)
        assert isinstance(event, BaseEvent)
