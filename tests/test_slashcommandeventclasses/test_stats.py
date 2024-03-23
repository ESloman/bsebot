"""Tests our Stats Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.stats import Stats
from tests.mocks.bsebot_mocks import BSEBotMock


class TestStats:
    """Tests our Stats commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.guild_ids = [123456, 65321]

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = Stats(self.client, self.guild_ids)
        assert isinstance(active, Stats)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.STATS
        assert active.help_string is not None
