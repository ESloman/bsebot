"""Tests our Awards class."""

import datetime
import random
from unittest import mock

import pytest

from discordbot.bot_enums import AwardsTypes, StatTypes
from discordbot.stats.statsdataclasses import StatDB
from mongo import interface
from mongo.bsedataclasses import Awards
from tests.mocks import interface_mocks

AWARD_CACHE: list[dict[str, any]] | None = None


def _get_award_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global AWARD_CACHE  # noqa: PLW0603
    if AWARD_CACHE is None:
        AWARD_CACHE = list(interface_mocks.query_mock("awards", {}))
    if not number:
        return AWARD_CACHE
    return random.choices(AWARD_CACHE, k=number)


class TestAwards:
    """Tests our Awards class."""

    def test_awards_init(self) -> None:
        """Tests Awards init."""
        awards = Awards()
        assert isinstance(awards, Awards)

    def test_awards_make_data_class(self) -> None:
        """Tests Awards make_data_class."""
        awards = Awards()
        data = _get_award_data()
        for entry in data:
            cls = awards.make_data_class(entry)
            assert isinstance(cls, StatDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_awards_document_stat(self) -> None:
        """Tests AWards document_stat."""
        awards = Awards()
        stat = awards.document_stat(
            123456, StatTypes.NUMBER_OF_MESSAGES, 500, datetime.datetime.now(), "most_messages", False, "Jan 24"
        )
        assert isinstance(stat, StatDB)

        kwargs = {"some": "data", "other": {"1": 1, "2": 2}}
        stat = awards.document_stat(
            123456,
            StatTypes.NUMBER_OF_MESSAGES,
            datetime.date.today(),
            datetime.datetime.now(),
            "most_messages",
            True,
            None,
            "2023",
            **kwargs,
        )
        assert isinstance(stat, StatDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_awards_document_award(self) -> None:
        """Tests AWards document_award."""
        awards = Awards()
        stat = awards.document_award(
            123456, AwardsTypes.BEST_AVG_WORDLE, 3.2, datetime.datetime.now(), "avg_wordle", False, "Jan 24"
        )
        assert isinstance(stat, StatDB)

        kwargs = {"some": "data", "other": {"1": 1, "2": 2}}
        stat = awards.document_stat(
            123456,
            AwardsTypes.BEST_AVG_WORDLE,
            datetime.date.today(),
            datetime.datetime.now(),
            "avg_wordle",
            True,
            None,
            "2023",
            **kwargs,
        )
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "entry", [Awards.make_data_class(entry) for entry in _get_award_data() if entry.get("month") == "Dec 23"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_awards_find_entry(self, entry: StatDB) -> None:
        """Tests Awards find_entry with monthly items."""
        awards = Awards()
        found = awards.find_entry(entry)
        assert isinstance(found, list)
        for item in found:
            assert isinstance(item, StatDB)
            assert entry == item

    @pytest.mark.parametrize(
        "entry", [Awards.make_data_class(entry) for entry in _get_award_data() if entry.get("year") == "2022"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_awards_find_entry_annual(self, entry: StatDB) -> None:
        """Tests Awards find_entry with annual items."""
        awards = Awards()
        found = awards.find_entry(entry)
        assert isinstance(found, list)
        for item in found:
            assert isinstance(item, StatDB)
            assert item == entry

    @pytest.mark.parametrize(
        "entry", [Awards.make_data_class(entry) for entry in _get_award_data() if entry.get("month") == "Dec 23"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_awards_find_previous_entry(self, entry: StatDB) -> None:
        """Tests Awards get_previous_stat with monthly items."""
        awards = Awards()
        found = awards.get_previous_stat(entry)
        assert isinstance(found, list)
        assert len(found) > 0
        for item in found:
            assert isinstance(item, StatDB)
            assert item != entry

    @pytest.mark.parametrize(
        "entry", [Awards.make_data_class(entry) for entry in _get_award_data() if entry.get("year") == "2023"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_awards_find_previous_entry_annual(self, entry: StatDB) -> None:
        """Tests Awards get_previous_stat with annual items."""
        awards = Awards()
        found = awards.get_previous_stat(entry)
        assert isinstance(found, list)
        for item in found:
            assert isinstance(item, StatDB)
            assert item != entry
