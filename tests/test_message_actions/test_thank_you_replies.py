"""Tests our ThankYouReplies message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.thank_you_replies import ThankYouReplies
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestThankYouReplies:
    """Tests our ThankYouReplies class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests init."""
        action = ThankYouReplies(self.client, self.logger)
        assert isinstance(action, BaseMessageAction)
