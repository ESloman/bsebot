"""Tests our Leaderboard Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.leaderboard import Leaderboard
from tests.mocks.bsebot_mocks import BSEBotMock


class TestLeaderboard:
    """Tests our Leaderboard commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = Leaderboard(self.client)
        assert isinstance(active, Leaderboard)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.BSEDDIES_LEADERBOARD
        assert active.help_string is not None
