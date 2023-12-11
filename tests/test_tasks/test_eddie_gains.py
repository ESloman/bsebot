"""Tests our eddie gains task."""

from unittest.mock import patch

import pytest

from discordbot.tasks.eddiegains import EddieGainMessager
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mock import BSEBotMock
from tests.mocks.mongo_mocks import GuildsMock, UserPointsMock
from tests.mocks.task_mocks import mock_eddie_manager_give_out_eddies
from tests.mocks.util_mocks import datetime_now


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
    async def test_execution(self) -> None:
        """Tests running the task."""
        task = EddieGainMessager(self.bsebot, [123], PlaceHolderLogger, [], start=False)

        with (
            patch.object(task.eddie_manager, "give_out_eddies", new=mock_eddie_manager_give_out_eddies),
            patch.object(task, "guilds", new=GuildsMock()),
            patch.object(task, "user_points", new=UserPointsMock()),
            patch("discordbot.tasks.eddiegains.datetime.datetime") as mock_datetime,
        ):
            mock_datetime.now.return_value = datetime_now(7, 30)

            result = await task.eddie_distributer()
            assert isinstance(result, list)
            assert len(result) > 0
