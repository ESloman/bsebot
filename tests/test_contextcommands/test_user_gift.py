"""Tests our ContextUserGift context command class."""

import pytest

from discordbot.contextcommands.base import BaseContextCommand
from discordbot.contextcommands.user_gift import ContextUserGift
from discordbot.slashcommandeventclasses.gift import Gift
from tests.mocks.bsebot_mocks import BSEBotMock


class TestContextUserGift:
    """Tests our ContextUserGift class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

        self.gift = Gift(self.client)

    def test_init(self) -> None:
        """Tests init."""
        command = ContextUserGift(self.client, self.gift)
        assert isinstance(command, BaseContextCommand)
