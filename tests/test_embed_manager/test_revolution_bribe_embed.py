"""Tests our revolution related functions in Embed Manager."""

import pytest

from discordbot.embedmanager import EmbedManager
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import interface_mocks


class TestRevolutionEmbed:
    """Class for testing revolution embed things."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        self.guild = Guilds.make_data_class(interface_mocks.mock_guild())
        self.event = RevolutionEvent.make_data_class(interface_mocks.mock_revolution_event())
        self.user = UserPoints.make_data_class(interface_mocks.mock_user())

    def test_get_revolution_bribe_message(self) -> None:
        """Tests our get_revolution_bribe_message with some standard parameters."""
        embeds = EmbedManager()
        message = embeds.get_revolution_bribe_message(self.guild, self.event, self.user, 2000)
        assert isinstance(message, str)
        assert len(message) < 2000
