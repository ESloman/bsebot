"""Tests our HighScore Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.highscore import HighScore
from tests.mocks.bsebot_mocks import BSEBotMock


class TestHighScore:
    """Tests our HighScore commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = HighScore(self.client)
        assert isinstance(active, HighScore)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.BSEDDIES_HIGHSCORES
        assert active.help_string is not None
