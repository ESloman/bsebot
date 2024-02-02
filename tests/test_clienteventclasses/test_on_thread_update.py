"""Tests our OnThreadUpdate client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onthreadupdate import OnThreadUpdate
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnThreadUpdate:
    """Tests our OnThreadUpdate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnThreadUpdate(self.client, [], self.logger)
        assert isinstance(event, OnThreadUpdate)
        assert isinstance(event, BaseEvent)
