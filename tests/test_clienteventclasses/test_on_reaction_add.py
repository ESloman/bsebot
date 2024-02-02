"""Tests our OnReactionAdd client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onreactionadd import OnReactionAdd
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnReactionAdd:
    """Tests our OnReactionAdd commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnReactionAdd(self.client, [], self.logger)
        assert isinstance(event, OnReactionAdd)
        assert isinstance(event, BaseEvent)
