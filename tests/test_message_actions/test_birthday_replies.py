"""Tests our BirthdayReplies message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.birthday_replies import BirthdayReplies
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestBirthdayReplies:
    """Tests our BirthdayReplies class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests init."""
        action = BirthdayReplies(self.client, self.logger)
        assert isinstance(action, BaseMessageAction)
