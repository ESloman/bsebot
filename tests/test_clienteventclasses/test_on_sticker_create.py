"""Tests our OnStickerCreate client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onstickercreate import OnStickerCreate
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnStickerCreate:
    """Tests our OnStickerCreate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnStickerCreate(self.client)
        assert isinstance(event, OnStickerCreate)
        assert isinstance(event, BaseEvent)
