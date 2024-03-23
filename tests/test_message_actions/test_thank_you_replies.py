"""Tests our ThankYouReplies message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.thank_you_replies import ThankYouReplies
from tests.mocks.bsebot_mocks import BSEBotMock


class TestThankYouReplies:
    """Tests our ThankYouReplies class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests init."""
        action = ThankYouReplies(self.client)
        assert isinstance(action, BaseMessageAction)
