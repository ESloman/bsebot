"""Tests our Active Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.active import Active
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from tests.mocks.bsebot_mocks import BSEBotMock


class TestActive:
    """Tests our Active commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.guild_ids = [123456, 65321]

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = Active(self.client, self.guild_ids)
        assert isinstance(active, Active)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.BSEDDIES_ACTIVE
        assert active.help_string is not None
