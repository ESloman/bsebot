"""Tests our reminder modals."""

from unittest import mock

import pytest

from discordbot.modals.reminder import ReminderModal
from mongo import interface
from mongo.bsepoints.guilds import Guilds
from tests.mocks import discord_mocks, interface_mocks


class TestReminderModal:
    """Tests our ReminderModal view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """

    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ReminderModal(0)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_callback(self, guild_data: dict[str, any]) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        reminder = ReminderModal(0)
        reminder.reminder_reason.value = "Some reason"
        reminder.reminder_timeout.value = "4h30m"
        guild = Guilds.make_data_class(guild_data)
        interaction = discord_mocks.InteractionMock(guild.guild_id, guild.owner_id)
        await reminder.callback(interaction)
