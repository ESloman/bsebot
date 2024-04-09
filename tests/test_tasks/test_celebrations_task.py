"""Tests our BetCloser task."""

import datetime
from unittest import mock
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from discordbot.constants import BSE_SERVER_ID
from discordbot.tasks.celebrations import Celebrations
from tests.mocks import bsebot_mocks


class TestCelebrations:
    """Tests our Celebrations class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        task = Celebrations(self.bsebot, [])
        assert not task.task.is_running()

        task = Celebrations(self.bsebot, [], True)
        assert task.task.is_running()

    @pytest.mark.parametrize("test_time", ["2024/01/01 19:30", "2024/12/25 7:00", "2024/12/25 9:00"])
    async def test_christmas_message_false(self, test_time: str) -> None:
        """Tests our christmas message trigger."""
        task = Celebrations(self.bsebot, [])
        with freeze_time(test_time):
            now = datetime.datetime.now(tz=ZoneInfo("UTC"))
            assert not await task._christmas_message(now, 123456)

    @freeze_time("2024/12/25 8:00")
    async def test_christmas_message_true(self) -> None:
        """Tests our christmas message trigger."""
        task = Celebrations(self.bsebot, [])
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        assert await task._christmas_message(now, 123456)

    @pytest.mark.parametrize("test_time", ["2024/01/01 01:00", "2024/12/25 7:00", "2024/12/25 9:00"])
    async def test_new_year_message_false(self, test_time: str) -> None:
        """Tests our new_year message trigger."""
        task = Celebrations(self.bsebot, [])
        with freeze_time(test_time):
            now = datetime.datetime.now(tz=ZoneInfo("UTC"))
            assert not await task._happy_new_year_message(now, 123456)

    @freeze_time("2024/01/01 0:00")
    async def test_new_year_message_true(self) -> None:
        """Tests our new_year message trigger."""
        task = Celebrations(self.bsebot, [])
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        assert await task._happy_new_year_message(now, 123456)

    @pytest.mark.parametrize("test_time", ["2024/02/11 9:00", "2024/02/11 11:00", "2024/12/25 9:00"])
    async def test_bsebot_birthday_message_false(self, test_time: str) -> None:
        """Tests our bsebot_birthday message trigger."""
        task = Celebrations(self.bsebot, [])
        with freeze_time(test_time):
            now = datetime.datetime.now(tz=ZoneInfo("UTC"))
            assert not await task._bsebot_birthday_message(now, 123456)

    @freeze_time("2024/02/11 10:00")
    async def test_bsebot_birthday_message_true(self) -> None:
        """Tests our bsebot_birthday message trigger."""
        task = Celebrations(self.bsebot, [])
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        assert await task._bsebot_birthday_message(now, 123456)

    @pytest.mark.parametrize("test_time", ["2024/05/14 9:00", "2024/05/14 11:00", "2024/12/25 9:00"])
    async def test_bse_birthday_message_false(self, test_time: str) -> None:
        """Tests our bse_birthday message trigger."""
        task = Celebrations(self.bsebot, [])
        with freeze_time(test_time):
            now = datetime.datetime.now(tz=ZoneInfo("UTC"))
            assert not await task._bse_birthday_message(now, 123456)

    @freeze_time("2024/05/14 10:00")
    async def test_bse_birthday_message_true(self) -> None:
        """Tests our bse_birthday message trigger."""
        task = Celebrations(self.bsebot, [])
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        assert await task._bse_birthday_message(now, 123456)

    async def test_celebrations(self) -> None:
        """Tests celebrations task."""
        bsebot = bsebot_mocks.BSEBotMock()
        bsebot._guilds = [{"guild_id": BSE_SERVER_ID, "owner_id": 123456, "name": "BSE Server"}]
        task = Celebrations(bsebot, [])
        with mock.patch.object(task.guilds, "get_channel", return_val=123456):
            await task.celebrations()

    async def test_celebrations_no_bse(self) -> None:
        """Tests celebrations task."""
        bsebot = bsebot_mocks.BSEBotMock()
        bsebot._guilds = []
        task = Celebrations(self.bsebot, [])
        with mock.patch.object(task.guilds, "get_channel", return_val=123456):
            await task.celebrations()
