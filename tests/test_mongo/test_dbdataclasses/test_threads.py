"""Tests our SpoilerThreads class."""

import datetime
import random
from unittest import mock

import pytest

from mongo import interface
from mongo.bsedataclasses import SpoilerThreads
from mongo.datatypes.thread import ThreadDB
from tests.mocks import interface_mocks

THREAD_CACHE: list[dict[str, any]] | None = None


def _get_thread_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global THREAD_CACHE  # noqa: PLW0603
    if THREAD_CACHE is None:
        THREAD_CACHE = list(interface_mocks.query_mock("spoilerthreads", {}))
    if not number:
        return THREAD_CACHE
    return random.choices(THREAD_CACHE, k=number)


class TestSpoilerThreads:
    """Tests our SpoilerThreads class."""

    def test_threads_init(self) -> None:
        """Tests SpoilerThreads init."""
        auto = SpoilerThreads()
        assert isinstance(auto, SpoilerThreads)

    def test_threads_make_data_class(self) -> None:
        """Tests SpoilerThreads make_data_class."""
        threads = SpoilerThreads()
        data = _get_thread_data()
        for entry in data:
            cls = threads.make_data_class(entry)
            assert isinstance(cls, ThreadDB)

    @pytest.mark.parametrize("guild_id", sorted({entry["guild_id"] for entry in _get_thread_data()}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_threads_get_all_threads(self, guild_id: int) -> None:
        """Tests SpoilerThreads get_all_threads."""
        threads = SpoilerThreads()
        all_threads = threads.get_all_threads(guild_id)
        assert isinstance(all_threads, list)
        for thread in all_threads:
            assert isinstance(thread, ThreadDB)

    @pytest.mark.parametrize(
        ("guild_id", "thread_id"), sorted({(entry["guild_id"], entry["thread_id"]) for entry in _get_thread_data()})
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_threads_get_thread_by_id(self, guild_id: int, thread_id: int) -> None:
        """Tests SpoilerThreads get_thread_by_id."""
        threads = SpoilerThreads()
        thread = threads.get_thread_by_id(guild_id, thread_id)
        assert isinstance(thread, ThreadDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_threads_get_thread_by_id_none(self) -> None:
        """Tests SpoilerThreads get_thread_by_id with an empty thread."""
        threads = SpoilerThreads()
        thread = threads.get_thread_by_id(123456, 123456)
        assert thread is None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_threads_insert_thread(self) -> None:
        """Tests SpoilerThreads insert thread."""
        threads = SpoilerThreads()
        thread = threads.insert_spoiler_thread(123456, 123, "some name", datetime.datetime.now(), 654321, 4)
        assert isinstance(thread, ThreadDB)
