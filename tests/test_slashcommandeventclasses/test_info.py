"""Tests our Active Slash Command class."""

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import BSE_SERVER_ID
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.info import Info
from tests.mocks import bsebot_mocks, discord_mocks


class TestActive:
    """Tests our Active commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        active = Info(self.client)
        assert isinstance(active, Info)
        assert isinstance(active, BSEddies)
        assert isinstance(active, BaseEvent)
        assert active.activity_type == ActivityTypes.INFO
        assert active.help_string is not None

    async def test_info(self) -> None:
        """Tests info command."""
        active = Info(self.client)
        ctx = discord_mocks.ContextMock(BSE_SERVER_ID)
        await active.info(ctx)
