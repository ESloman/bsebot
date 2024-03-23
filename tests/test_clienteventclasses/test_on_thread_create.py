"""Tests our OnThreadCreate client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onthreadcreate import OnThreadCreate
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnThreadCreate:
    """Tests our OnThreadCreate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnThreadCreate(self.client, [])
        assert isinstance(event, OnThreadCreate)
        assert isinstance(event, BaseEvent)
