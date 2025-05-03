"""Tests our bet reminder task."""

import datetime
import operator
from typing import TYPE_CHECKING
from unittest import mock
from zoneinfo import ZoneInfo

import pytest

from discordbot.tasks.betreminder import BetReminder
from mongo import interface
from mongo.bsepoints.bets import UserBets
from tests.mocks import bsebot_mocks, interface_mocks

if TYPE_CHECKING:
    from mongo.datatypes.bet import BetDB


@pytest.mark.xfail
class TestBetReminder:
    """Tests our BetReminder class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = BetReminder(self.bsebot, [], start=False)

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_day_reminder(self, bet_data: dict) -> None:
        """Tests check_for_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_data["timeout"] = now + datetime.timedelta(hours=23)
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_day_reminder(bet_db, now)
        assert success

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_day_reminder_already_gone(self, bet_data: dict) -> None:
        """Tests check_for_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_day_reminder(bet_db, now)
        assert not success

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_day_reminder_not_yet(self, bet_data: dict) -> None:
        """Tests check_for_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_data["timeout"] = now + datetime.timedelta(hours=30)
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_day_reminder(bet_db, now)
        assert not success

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_half_day_reminder(self, bet_data: dict) -> None:
        """Tests check_for_half_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_data["created"] = now - datetime.timedelta(hours=5)
        bet_data["timeout"] = now + datetime.timedelta(hours=30)
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_halfway_reminder(bet_db, now)
        assert not success

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_half_day_reminder_success(self, bet_data: dict) -> None:
        """Tests check_for_half_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_data["created"] = now - datetime.timedelta(days=10, hours=12)
        bet_data["timeout"] = now + datetime.timedelta(days=10, hours=13)
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_halfway_reminder(bet_db, now)
        assert success

    @pytest.mark.parametrize(
        "bet_data", sorted(interface_mocks.query_mock("userbets", {})[-10:], key=operator.itemgetter("bet_id"))
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_for_half_day_reminder_gone(self, bet_data: dict) -> None:
        """Tests check_for_half_day_reminder function."""
        task = BetReminder(self.bsebot, [], start=False)
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        bet_data["active"] = True
        bet_data["created"] = now - datetime.timedelta(days=10, hours=12)
        bet_data["timeout"] = now + datetime.timedelta(days=1, hours=13)
        bet_db: BetDB = UserBets.make_data_class(bet_data)
        success = await task._check_bet_for_halfway_reminder(bet_db, now)
        assert not success

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_default_execution(self) -> None:
        """Tests default execution."""
        task = BetReminder(self.bsebot, [], start=False)
        await task.bet_reminder()
