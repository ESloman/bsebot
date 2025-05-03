"""Tests our BetCloser task."""

import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import pytest

from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.tasks.betcloser import BetCloser
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, interface_mocks


@pytest.mark.xfail
class TestBetCloser:
    """Tests our BetCloser class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

        self.place = PlaceBet(self.bsebot)
        self.close = CloseBet(self.bsebot)

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = BetCloser(self.bsebot, [], self.place, self.close, start=False)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_execution(self) -> None:
        """Tests if we can execute task."""
        closer = BetCloser(self.bsebot, [], self.place, self.close, start=False)
        await closer.bet_closer()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution_with_timed_out_bets(self) -> None:
        """Tests if we can execute task."""
        closer = BetCloser(self.bsebot, [], self.place, self.close, start=False)
        bet_datas = interface_mocks.query_mock("userbets", {})[-5:]
        for bet in bet_datas:
            bet["active"] = True
            bet["timeout"] = datetime.datetime.now(tz=ZoneInfo("UTC")) - datetime.timedelta(days=2)
        bets = [UserBets.make_data_class(b) for b in bet_datas]
        with mock.patch.object(closer.user_bets, "get_all_active_bets", return_value=bets):
            await closer.bet_closer()
