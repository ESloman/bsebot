"""Tests our TicketedEvents classes."""

import datetime
import random
from unittest import mock

import pytest

from mongo import interface
from mongo.bseticketedevents import RevolutionEvent
from mongo.datatypes.revolution import RevolutionEventDB
from tests.mocks import interface_mocks

EVENT_CACHE: list[dict[str, any]] | None = None


def _get_event_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global EVENT_CACHE  # noqa: PLW0603
    if EVENT_CACHE is None:
        EVENT_CACHE = list(interface_mocks.query_mock("ticketedevents", {}))
    if not number:
        return EVENT_CACHE
    return random.choices(EVENT_CACHE, k=number)


class TestRevolutionEvent:
    """Tests our RevolutionEvent class."""

    def test_revolution_events_init(self) -> None:
        """Tests RevolutionEvent init."""
        revolutions = RevolutionEvent()
        assert isinstance(revolutions, RevolutionEvent)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_revolution_events_create_counter_doc(self) -> None:
        """Tests RevolutionEvent _create_counter_doc."""
        revolutions = RevolutionEvent()
        with mock.patch.object(revolutions, "query", return_val=True):
            revolutions._create_counter_document(123456)
        with mock.patch.object(revolutions, "query", return_val=False):
            revolutions._create_counter_document(654321)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=lambda *_args, **_kwargs: [{"count": 12}])  # noqa: PT008, ARG005
    @mock.patch.object(interface, "update", new=interface_mocks.insert_mock)
    def test_revolution_events_get_new_id(self) -> None:
        """Tests RevolutionEvent _get_new_id."""
        revolutions = RevolutionEvent()
        with mock.patch.object(revolutions, "_create_counter_document", return_val=None):
            count = revolutions._get_new_id(123456)
            assert isinstance(count, str)
            assert count == "012"

    def test_revolutions_make_data_class(self) -> None:
        """Tests RevolutionEvent make_data_class."""
        revolutions = RevolutionEvent()
        data = _get_event_data()
        for entry in data:
            if "type" in entry:
                continue
            cls = revolutions.make_data_class(entry)
            assert isinstance(cls, RevolutionEventDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_event_data()})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_revolutions_create_event(self, guild_id: int) -> None:
        """Tests RevolutionEvent create_event."""
        revolutions = RevolutionEvent()
        with mock.patch.object(revolutions, "_get_new_id", return_val="200"):
            revolutions.create_event(
                guild_id,
                datetime.datetime.now(),
                datetime.datetime.now() + datetime.timedelta(hours=2),
                654321,
                1000,
                246810,
            )
