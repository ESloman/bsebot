"""Tests our eddie gains task."""

from unittest import mock

import discord
import pytest

from discordbot.tasks.activitychanger import ActivityChanger
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from tests.mocks import bsebot_mocks, interface_mocks


class TestActivityChanger:
    """Tests our ActivityChanger class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = ActivityChanger(self.bsebot, [], self.logger, [], start=False)

    async def test_execution_default(self) -> None:
        """Tests running the task with the default activity."""
        task = ActivityChanger(self.bsebot, [], self.logger, [], start=False)
        with mock.patch("random.random", return_value=0.1):
            # should always set the default activity
            activity: discord.Activity = await task.activity_changer()
        assert activity.name == "conversations"
        assert activity.state == "Listening"
        assert activity.type == discord.ActivityType.listening
        assert activity.details == "Waiting for commands!"
        assert activity is task.default_activity

    @pytest.mark.parametrize("exc_times", list(range(10)))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_execution_change(self, exc_times: int) -> None:
        """Tests running the task where we pick an activity from the pool."""
        task = ActivityChanger(self.bsebot, [], self.logger, [], start=False)
        with mock.patch("random.random", return_value=0.95):
            # should always set the default activity
            activity: discord.Activity = await task.activity_changer()
        assert activity is not task.default_activity
        assert activity != task.default_activity
