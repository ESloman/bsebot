"""Tests our eddie gains task."""

import datetime
from collections import Counter
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from discordbot.tasks.eddiegains import BSEddiesManager, EddieGainMessager
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock
from tests.mocks.mongo_mocks import GuildsMock, UserPointsMock
from tests.mocks.task_mocks import mock_bseddies_manager_counters, mock_eddie_manager_give_out_eddies


class TestEddieGainMessager:
    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = EddieGainMessager(self.bsebot, [], PlaceHolderLogger, [], start=False)

    @pytest.mark.asyncio()
    async def test_not_execution_time(self) -> None:
        """Tests if running the task with the wrong time exits."""
        task = EddieGainMessager(self.bsebot, [], PlaceHolderLogger, [], start=False)

        result = await task.eddie_distributer()
        assert result is None

    @pytest.mark.asyncio()
    @freeze_time("2024-01-01 07:30:01")
    async def test_execution(self) -> None:
        """Tests running the task."""
        task = EddieGainMessager(self.bsebot, [123], PlaceHolderLogger, [], start=False)

        with (
            patch.object(task.eddie_manager, "give_out_eddies", new=mock_eddie_manager_give_out_eddies),
            patch.object(task, "guilds", new=GuildsMock()),
            patch.object(task, "user_points", new=UserPointsMock()),
        ):
            result = await task.eddie_distributer()
            assert isinstance(result, list)
            assert len(result) > 0


class TestBSEddiesManager:
    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = BSEddiesManager(self.bsebot, [], PlaceHolderLogger, [])

    @pytest.mark.parametrize("days", [1, 2, 3, 4, 5, 10])
    def test_get_datetime_objects(self, days: int) -> None:
        """Tests our get_datetime_objects method."""
        now = datetime.datetime.now()
        manager = BSEddiesManager(self.bsebot, [], PlaceHolderLogger, [])
        start, end = manager.get_datetime_objects(days)

        for obj in (start, end):
            assert isinstance(obj, datetime.datetime)
            assert obj < now
            assert obj.day == (now - datetime.timedelta(days=days)).day

    @pytest.mark.parametrize(("counter", "start", "expected"), mock_bseddies_manager_counters())
    def test_calc_eddies(self, counter: Counter, start: int, expected: float) -> None:
        """Tests our _calc_eddies method."""
        manager = BSEddiesManager(self.bsebot, [], PlaceHolderLogger, [])
        eddies = manager._calc_eddies(counter, start)
        assert eddies == expected
