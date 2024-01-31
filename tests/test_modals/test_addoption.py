"""Tests our addoption modals."""

from unittest import mock

import pytest

from discordbot.constants import CREATOR
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.config import ConfigView
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestAddOption:
    """Tests our AddOption view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    @pytest.mark.parametrize("bet_data", interface_mocks.query_mock("userbets", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self, bet_data: dict) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = UserBets.make_data_class(bet_data)
