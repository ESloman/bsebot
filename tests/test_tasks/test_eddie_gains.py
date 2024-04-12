"""Tests our eddie gains task."""

import datetime
from collections import Counter
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from discordbot.tasks.eddiegains import BSEddiesManager, EddieGainMessager
from mongo import interface
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
            assert isinstance(result, list)
            assert len(result) > 0

    @freeze_time("2024-01-01 07:30:01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution(self) -> None:
        """Tests running the task."""
        task = EddieGainMessager(self.bsebot, [123], start=False)

        with (
            mock.patch.object(task.eddie_manager, "give_out_eddies", new=task_mocks.mock_eddie_manager_give_out_eddies),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, list)
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
