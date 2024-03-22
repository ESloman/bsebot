"""Tests our revolution bribe view."""

from unittest import mock

import pytest

from discordbot.utilities import PlaceHolderLogger
from discordbot.views.revolutionbribeview import RevolutionBribeView
from mongo import interface
from mongo.bseticketedevents import RevolutionEvent
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestRevolutionBribeView:
    """Tests our RevolutionBribeView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        event_data = interface_mocks.query_mock("ticketedevents", {})[-1]
        _ = RevolutionBribeView(self.bsebot, RevolutionEvent.make_data_class(event_data), 500, self.logger)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_accept_callback(self) -> None:
        """Tests accept callback."""
        event_data = interface_mocks.query_mock("ticketedevents", {})[-1]
        event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionBribeView(self.bsebot, event, 500, self.logger)
        interaction = discord_mocks.InteractionMock(event.guild_id, event.king)
        await view.accept_callback.callback(interaction)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_refuse_callback(self) -> None:
        """Tests refuse callback."""
        event_data = interface_mocks.query_mock("ticketedevents", {})[-1]
        event = RevolutionEvent.make_data_class(event_data)
        view = RevolutionBribeView(self.bsebot, event, 500, self.logger)
        interaction = discord_mocks.InteractionMock(event.guild_id, event.king)
        await view.refuse_callback.callback(interaction)
