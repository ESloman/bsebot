"""Tests our activity changer task."""

from unittest import mock

import discord
import pytest

from discordbot.tasks.activitychanger import ActivityChanger
from mongo.datatypes.botactivities import BotActivityDB
from tests.mocks import bsebot_mocks, interface_mocks


class TestActivityChanger:
    """Tests our ActivityChanger class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = ActivityChanger(self.bsebot, [], start=False)

    async def test_execution_default(self) -> None:
        """Tests running the task with the default activity."""
        task = ActivityChanger(self.bsebot, [], start=False)
        with (
            mock.patch("random.random", return_value=0.1),
            mock.patch.object(task.bot_activities, "get_all_activities") as get_all_activities,
        ):
            # should always set the default activity
            activity: discord.Activity = await task.activity_changer()
        assert activity.name == "conversations"
        assert activity.state == "Listening"
        assert activity.type == discord.ActivityType.listening
        assert activity.details == "Waiting for commands!"
        assert activity is task.default_activity
        assert not get_all_activities.call_count

    @pytest.mark.parametrize("category", ["playing", "listening", "watching"])
    async def test_execution_change(self, category: str) -> None:
        """Tests running the task where we pick an activity from the pool."""
        task = ActivityChanger(self.bsebot, [], start=False)
        with (
            mock.patch("random.random", return_value=0.95),
            mock.patch.object(task.bot_activities, "get_all_activities") as get_all_activities,
            mock.patch.object(task.bot_activities, "update") as update,
        ):
            get_all_activities.return_value = [
                BotActivityDB(**interface_mocks.mock_bot_activity(category=category)),
                BotActivityDB(**interface_mocks.mock_bot_activity(category=category)),
            ]
            # should always set the default activity
            activity: discord.Activity = await task.activity_changer()
        assert activity is not None
        assert activity is not task.default_activity
        assert activity != task.default_activity
        assert activity.state == category.title()
        assert activity.type == discord.ActivityType[category]

        get_all_activities.assert_called_once()
        update.assert_called_once()
