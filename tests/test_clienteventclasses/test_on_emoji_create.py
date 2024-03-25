"""Tests our OnEmojiCreate client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onemojicreate import OnEmojiCreate
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnEmojiCreate:
    """Tests our OnEmojiCreate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnEmojiCreate(self.client)
        assert isinstance(event, OnEmojiCreate)
        assert isinstance(event, BaseEvent)
