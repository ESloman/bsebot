"""Tests our DuplicateLinkAction message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.duplicate_links import DuplicateLinkAction
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestDuplicateLinkAction:
    """Tests our DuplicateLinkAction class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests init."""
        action = DuplicateLinkAction(self.client, self.logger)
        assert isinstance(action, BaseMessageAction)
