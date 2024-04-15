"""Tests our eddie gains task."""

import copy
import datetime
import random
from collections import Counter
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from discordbot.constants import HUMAN_MESSAGE_TYPES
from discordbot.tasks.eddiegains import BSEddiesManager, EddieGainMessager
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.user import UserDB
from tests.mocks import bsebot_mocks, interface_mocks, task_mocks


class TestEddieGainMessager:
    """Tests our EddieGainMessager class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = EddieGainMessager(self.bsebot, [], start=False)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_format_detailed_breakdown_message_part(self) -> None:
        """Tests formatting a breakdown."""
        task = EddieGainMessager(self.bsebot, [], start=False)
        breakdown = dict.fromkeys(HUMAN_MESSAGE_TYPES, int(random.random() * random.randint(1, 100)))
        message = task._format_detailed_breakdown_message_part(breakdown, "My cool guild")
        assert isinstance(message, str)
        assert "### My cool guild" in message
        for value in HUMAN_MESSAGE_TYPES.values():
            assert value in message

    @freeze_time("2024-01-01 04:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_check_salary_time_false(self) -> None:
        """Tests checking salary time when there's still time to trigger."""
        task = EddieGainMessager(self.bsebot, [], start=False)
        with mock.patch.object(task.guilds, "get_all_guilds") as get_all_guilds:
            assert task._check_salary_time() is None
            assert not get_all_guilds.call_count

    @freeze_time("2024-01-01 08:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_check_salary_time(self) -> None:
        """Tests checking salary time when there's still time to trigger."""
        # setup
        guilds = [copy.deepcopy(guild) for guild in interface_mocks.query_mock("guilds", {})]
        assert len(guilds) >= 2
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        guilds[0]["last_salary_time"] = now.replace(hour=7, minute=30)
        guilds[1]["last_salary_time"] = now - datetime.timedelta(days=1)
        guild_dbs = [Guilds.make_data_class(guild) for guild in guilds]
        task = EddieGainMessager(self.bsebot, [], start=False)
        task.schedule.overriden = False
        with mock.patch.object(task.guilds, "get_all_guilds", new=lambda: guild_dbs):  # noqa: PT008
            task._check_salary_time()
            assert task.schedule.overriden

    @freeze_time("2024-01-01 08:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_not_execution_time(self) -> None:
        """Tests if running the task with the wrong time exits."""
        task = EddieGainMessager(self.bsebot, [], start=False)
        task.schedule.overriden = False
        result = await task.eddie_distributer()
        assert result is None

    @freeze_time("2024-01-01 08:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_not_execution_time_overriden(self) -> None:
        """Tests if running the task with the wrong time but overriden works."""
        task = EddieGainMessager(self.bsebot, [], start=False)
        task.schedule.overriden = True
        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, dict)
            assert len(result) > 0

    @freeze_time("2024-01-01 07:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution(self) -> None:
        """Tests running the task."""
        task = EddieGainMessager(self.bsebot, [], start=False)

        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, dict)
            assert len(result) > 0

    @freeze_time("2024-01-01 07:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution_enable_daily_eddies(self) -> None:
        """Tests running the task but ensuring daily_eddies is set."""
        task = EddieGainMessager(self.bsebot, [], start=False)

        def _find_user_replacement(user_id: int, guild_id: int) -> UserDB | None:
            try:
                user = interface_mocks.query_mock("userpoints", {"uid": user_id, "guild_id": guild_id})[0]
            except IndexError:
                return None
            user["daily_eddies"] = True
            return UserPoints.make_data_class(user)

        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
            mock.patch.object(task.user_points, "find_user", new=_find_user_replacement),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, dict)
            assert len(result) > 0

    @freeze_time("2024-01-01 07:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution_enable_disable_daily_eddies(self) -> None:
        """Tests running the task but ensuring daily_eddies is not set."""
        task = EddieGainMessager(self.bsebot, [], start=False)

        def _find_user_replacement(user_id: int, guild_id: int) -> UserDB | None:
            try:
                user = interface_mocks.query_mock("userpoints", {"uid": user_id, "guild_id": guild_id})[0]
            except IndexError:
                return None
            user["daily_eddies"] = False
            return UserPoints.make_data_class(user)

        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
            mock.patch.object(task.user_points, "find_user", new=_find_user_replacement),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, dict)
            assert len(result) > 0

    @freeze_time("2024-01-01 07:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution_enable_enable_detailed_mode(self) -> None:
        """Tests running the task but ensuring detailed mode is set."""
        task = EddieGainMessager(self.bsebot, [], start=False)

        def _find_user_replacement(user_id: int, guild_id: int) -> UserDB | None:
            try:
                user = interface_mocks.query_mock("userpoints", {"uid": user_id, "guild_id": guild_id})[0]
            except IndexError:
                return None
            user["daily_eddies"] = True
            user["summary_detailed_mode"] = True
            return UserPoints.make_data_class(user)

        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
            mock.patch.object(task.user_points, "find_user", new=_find_user_replacement),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, dict)
            assert len(result) > 0


class TestBSEddiesManager:
    """Tests our BSEddiesManager class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = BSEddiesManager(self.bsebot, [])

    @pytest.mark.parametrize("days", [1, 2, 3, 4, 5, 10])
    def test_get_datetime_objects(self, days: int) -> None:
        """Tests our get_datetime_objects method."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        manager = BSEddiesManager(self.bsebot, [])
        start, end = manager.get_datetime_objects(days)

        for obj in (start, end):
            assert isinstance(obj, datetime.datetime)
            assert obj < now
            assert obj.day == (now - datetime.timedelta(days=days)).day

    @pytest.mark.parametrize(("counter", "start", "expected"), task_mocks.mock_bseddies_manager_counters())
    def test_calc_eddies(self, counter: Counter, start: int, expected: float) -> None:
        """Tests our _calc_eddies method."""
        manager = BSEddiesManager(self.bsebot, [])
        eddies = manager._calc_eddies(counter, start)
        assert eddies == expected

    @pytest.mark.parametrize(
        ("guild_id", "date"),
        [
            (gid, date)
            for gid in {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})}
            for date in ["2023-12-02", "2023-12-25", "2023-12-31"]
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_give_out_eddies_predict(self, guild_id: int, date: str) -> None:
        """Tests our give_out_eddies method."""
        with freeze_time(date):
            manager = BSEddiesManager(self.bsebot, [])
            results = manager.give_out_eddies(guild_id, False)
        assert isinstance(results, dict)

    @pytest.mark.parametrize(
        ("guild_id", "date"),
        [
            (gid, date)
            for gid in {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})}
            for date in ["2023-12-02", "2023-12-25", "2023-12-31"]
        ],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_give_out_eddies_real(self, guild_id: int, date: str) -> None:
        """Tests our give_out_eddies method."""
        with freeze_time(date):
            manager = BSEddiesManager(self.bsebot, [])
            results = manager.give_out_eddies(guild_id, True)
        assert isinstance(results, dict)
