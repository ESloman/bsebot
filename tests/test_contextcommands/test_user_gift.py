"""Tests our ContextUserGift context command class."""

import pytest

from discordbot.contextcommands.base import BaseContextCommand
from discordbot.contextcommands.user_gift import ContextUserGift
from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestContextUserGift:
    """Tests our ContextUserGift class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger
        self.gift = Gift(self.client, [], self.logger)

    def test_init(self) -> None:
        """Tests init."""
        command = ContextUserGift(self.client, [], self.logger, self.gift)
        assert isinstance(command, BaseContextCommand)
