"""Tests our OnStickerCreate client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onstickercreate import OnStickerCreate
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnStickerCreate:
    """Tests our OnStickerCreate commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnStickerCreate(self.client, [], self.logger)
        assert isinstance(event, OnStickerCreate)
        assert isinstance(event, BaseEvent)
