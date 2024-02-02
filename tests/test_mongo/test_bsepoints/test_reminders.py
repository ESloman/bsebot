"""Tests our UserReminders class."""

import datetime
import random
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.reminders import ServerReminders
from mongo.datatypes.reminder import ReminderDB
from tests.mocks import interface_mocks

REMINDER_CACHE: list[dict[str, any]] | None = None


def _get_reminder_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global REMINDER_CACHE  # noqa: PLW0603
    if REMINDER_CACHE is None:
        REMINDER_CACHE = list(interface_mocks.query_mock("reminders", {}))
    if not number:
        return REMINDER_CACHE
    return random.choices(REMINDER_CACHE, k=number)


class TestServerReminders:
    """Tests our ServerReminders class."""

    def test_reminders_init(self) -> None:
        """Tests ServerReminders init."""
        reminders = ServerReminders()
        assert isinstance(reminders, ServerReminders)

    def test_reminders_make_data_class(self) -> None:
        """Tests ServerReminders make_data_class."""
        for reminder in _get_reminder_data():
            rem_db = ServerReminders.make_data_class(reminder)
            assert isinstance(rem_db, ReminderDB)

    @pytest.mark.parametrize("guild_id", sorted({entry["guild_id"] for entry in _get_reminder_data()}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_get_all_reminders(self, guild_id: int) -> None:
        """Tests ServerReminders get open reminders."""
        reminders = ServerReminders()
        open_reminders = reminders.get_open_reminders(guild_id)
        assert isinstance(open_reminders, list)
        for reminder in open_reminders:
            assert isinstance(reminder, ReminderDB)

    @pytest.mark.parametrize("object_id", sorted({entry["_id"] for entry in _get_reminder_data()}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_close_reminder(self, object_id: int) -> None:
        """Tests ServerReminders close_reminder."""
        reminders = ServerReminders()
        reminders.close_reminder(object_id)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_insert_reminder(self) -> None:
        """Tests ServerReminders insert_reminder."""
        reminders = ServerReminders()
        reminders.insert_reminder(
            123,
            456,
            datetime.datetime.now(),
            datetime.datetime.now() + datetime.timedelta(minutes=5),
            "",
            123456,
            654321,
        )
