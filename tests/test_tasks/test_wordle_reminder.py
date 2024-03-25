"""Tests our wordle reminder task."""

import datetime
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from discordbot.tasks.wordlereminder import WordleReminder
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.message import MessageDB
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestWordleReminder:
    """Tests our WordleReminder class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests if we can initialise the task."""
        _ = WordleReminder(self.bsebot, [], start=False)

    @freeze_time("2024/01/29 13:00")
    async def test_default_execution(self) -> None:
        """Tests that we don't trigger on the wrong time."""
        task = WordleReminder(self.bsebot, [], start=False)
        await task.wordle_reminder()

    @freeze_time("2024/01/01 19:30")
    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_reminders_no_reminders(self, guild_data: dict[str, any]) -> None:
        """Tests get_reminders where we should find no reminders needed."""
        task = WordleReminder(self.bsebot, [], start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        start = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)
        reminders = task._get_reminders_needed(guild, start, end)
        assert isinstance(reminders, list)
        assert len(reminders) == 0

    @freeze_time("2024/01/01 19:30")
    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_reminders_no_reminders_config(self, guild_data: dict[str, any]) -> None:
        """Tests get_reminders where the guild isn't configured for reminders."""
        task = WordleReminder(self.bsebot, [], start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        start = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)

        def _mock_get_guild(guild_id: int) -> GuildDB:
            """Mock get guild to set wordle_reminders to False."""
            _guild = interface_mocks.query_mock("guilds", {"guild_id": guild_id})[0]
            _guild["wordle_reminders"] = False
            return Guilds.make_data_class(_guild)

        with mock.patch.object(task.guilds, "get_guild", new=_mock_get_guild):
            reminders = task._get_reminders_needed(guild, start, end)
        assert isinstance(reminders, list)
        assert len(reminders) == 0

    @freeze_time("2024/01/08 19:30")
    @pytest.mark.parametrize(
        "guild_data", sorted(interface_mocks.query_mock("guilds", {}), key=lambda x: x["guild_id"])
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_reminders_reminders(self, guild_data: dict[str, any]) -> None:
        """Tests get_reminders where we should find reminders needed."""
        task = WordleReminder(self.bsebot, [], start=False)
        guild = discord_mocks.GuildMock(guild_data["guild_id"], guild_data["owner_id"], guild_data["name"])
        start = datetime.datetime.now(tz=pytz.utc) - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)
        reminders = task._get_reminders_needed(guild, start, end)
        assert isinstance(reminders, list)
        assert len(reminders) > 0
        for reminder in reminders:
            assert isinstance(reminder, MessageDB)

    @freeze_time("2024/01/01 19:30")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_default_execution_no_reminders(self) -> None:
        """Tests execution with a day that had wordles done successfully."""
        task = WordleReminder(self.bsebot, [], start=False)
        await task.wordle_reminder()

    @freeze_time("2024/01/08 19:30")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_default_execution_reminders(self) -> None:
        """Tests execution where reminders are needed."""
        task = WordleReminder(self.bsebot, [], start=False)
        await task.wordle_reminder()
