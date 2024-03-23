"""Tests our MarvelComicsAdAction message action class."""

import pytest

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.marvel_ad import MarvelComicsAdAction
from tests.mocks.bsebot_mocks import BSEBotMock


class TestMarvelComicsAdAction:
    """Tests our MarvelComicsAdAction class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests init."""
        action = MarvelComicsAdAction(self.client)
        assert isinstance(action, BaseMessageAction)
