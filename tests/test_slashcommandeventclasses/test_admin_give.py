"""Tests our AdminGive Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.admin_give import AdminGive
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from tests.mocks.bsebot_mocks import BSEBotMock


class TestAdminGive:
    """Tests our AdminGive commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()
        self.guild_ids = [123456, 65321]

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = AdminGive(self.client, self.guild_ids)
        assert isinstance(active, AdminGive)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.BSEDDIES_ADMIN_GIVE
        assert active.help_string is not None
