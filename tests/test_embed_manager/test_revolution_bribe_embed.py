"""Tests our revolution related functions in Embed Manager."""

import pytest

from discordbot.embedmanager import EmbedManager
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import interface_mocks


class TestRevolutionEmbed:
    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        self.guild = Guilds.make_data_class(interface_mocks.query_mock("guilds", {"revolution": True})[0])
        self.event = RevolutionEvent.make_data_class(
            interface_mocks.query_mock("ticketedevents", {"type": "revolution"})[-1]
        )
        self.user = UserPoints.make_data_class(interface_mocks.query_mock("userpoints", {"uid": self.event.king})[-1])

    def test_get_revolution_bribe_message(self) -> None:
        """Tests our get_revolution_bribe_message with some standard parameters."""
        embeds = EmbedManager()
        message = embeds.get_revolution_bribe_message(self.guild, self.event, self.user, 2000)
        assert isinstance(message, str)
