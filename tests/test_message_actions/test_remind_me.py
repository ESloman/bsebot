"""Tests our RemindMeAction message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.remind_me import RemindMeAction
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestRemindMeAction:
    """Tests our RemindMeAction class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests init."""
        action = RemindMeAction(self.client, self.logger)
        assert isinstance(action, BaseMessageAction)
