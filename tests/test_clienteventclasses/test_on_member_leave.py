"""Tests our OnMemberLeave client event class."""

import pytest

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onmemberleave import OnMemberLeave
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestOnMemberLeave:
    """Tests our OnMemberLeave commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnMemberLeave(self.client, [], self.logger)
        assert isinstance(event, OnMemberLeave)
        assert isinstance(event, BaseEvent)
