"""Tests the StatsDataCache class."""

import datetime
import random
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from discordbot.stats.statsclasses import StatsGatherer
from discordbot.stats.statsdataclasses import StatDB
from discordbot.utilities import PlaceHolderLogger
from mongo import interface
from mongo.bsedataclasses import Awards
from tests.mocks import interface_mocks

INTERACTION_CACHE: list[dict[str, any]] | None = None
AWARD_CACHE: list[dict[str, any]] | None = None


def _get_award_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global AWARD_CACHE  # noqa: PLW0603
    if AWARD_CACHE is None:
        AWARD_CACHE = list(interface_mocks.query_mock("awards", {}))
    if not number:
        return AWARD_CACHE
    return random.choices(AWARD_CACHE, k=number)


def _get_interaction_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global INTERACTION_CACHE  # noqa: PLW0603
    if INTERACTION_CACHE is None:
        INTERACTION_CACHE = list(interface_mocks.query_mock("userinteractions", {}))
    if not number:
        return INTERACTION_CACHE
    return random.choices(INTERACTION_CACHE, k=number)


class TestsStatsGatherer:
    """Tests our StatsGatherer class."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.logger = PlaceHolderLogger

    def test_stats_gatherer_init_defaults(self) -> None:
        """Tests StatsGatherer init."""
        stats = StatsGatherer(self.logger)
        assert isinstance(stats, StatsGatherer)
        assert not stats.annual

    def test_stats_gatherer_init_non_defaults(self) -> None:
        """Tests StatsGatherer init."""
        stats = StatsGatherer(self.logger, True)
        assert isinstance(stats, StatsGatherer)
        assert stats.annual

    @freeze_time("2024-01-01")
    def test_stats_get_monthly_datetime(self) -> None:
        """Tests StatsGatherer get_monthly_datetime_objects."""
        stats = StatsGatherer(self.logger)
        start, end = stats.get_monthly_datetime_objects()
        assert isinstance(start, datetime.datetime)
        assert isinstance(end, datetime.datetime)

        # test start
        assert start.year == 2023
        assert start.month == 12
        assert start.day == 1
        assert start.hour == 0
        assert start.minute == 0

        assert end.year == 2024
        assert end.month == 1
        assert end.day == 1
        assert end.hour == 0

    @freeze_time("2024-01-01")
    def test_stats_get_annual_datetime(self) -> None:
        """Tests StatsGatherer get_annual_datetime_objects."""
        stats = StatsGatherer(self.logger, True)
        start, end = stats.get_annual_datetime_objects()
        assert isinstance(start, datetime.datetime)
        assert isinstance(end, datetime.datetime)

        # test start
        assert start.year == 2023
        assert start.month == 1
        assert start.day == 1
        assert start.hour == 0
        assert start.minute == 0

        assert end.year == 2024
        assert end.month == 1
        assert end.day == 1
        assert end.hour == 0

    @freeze_time("2024-01-01")
    @pytest.mark.parametrize(
        "entry", [Awards.make_data_class(entry) for entry in _get_award_data() if entry.get("month") == "Dec 23"]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_add_annual_changes(self, entry: StatDB) -> None:
        """Tests StatsGatherer add_annual_changes."""
        stats = StatsGatherer(self.logger)
        start, _ = stats.get_monthly_datetime_objects()
        new_entry = stats.add_annual_changes(start, entry)
        # shouldn't be changed
        assert new_entry is entry
        assert not new_entry.annual

        annual_stats = StatsGatherer(self.logger, True)
        new_entry = annual_stats.add_annual_changes(start, entry)
        # shouldn't be changed
        assert new_entry is not entry
        assert new_entry.annual
        assert new_entry.year == "2023"


class TestsStatsGathererStatsMethods:
    """Tests our StatsGatherer class and it's actual stats methods."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.logger = PlaceHolderLogger
        now = datetime.datetime.now(tz=pytz.utc)
        self.start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        self.end = self.start.replace(year=2024, month=1)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_messages(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_messages."""
        stats = StatsGatherer(self.logger)
        messages_stats = stats.number_of_messages(guild_id, self.start, self.end)
        assert isinstance(messages_stats, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_threaded_messages(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_threaded_messages."""
        stats = StatsGatherer(self.logger)
        messages_stats = stats.number_of_threaded_messages(guild_id, self.start, self.end)
        assert isinstance(messages_stats, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_average_message_length(self, guild_id: int) -> None:
        """Tests StatsGatherer average_message_length."""
        stats = StatsGatherer(self.logger)
        character_stats, word_stats = stats.average_message_length(guild_id, self.start, self.end)
        assert isinstance(character_stats, StatDB)
        assert isinstance(word_stats, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_channel(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_channel."""
        stats = StatsGatherer(self.logger)
        channel_stat = stats.busiest_channel(guild_id, self.start, self.end)
        assert isinstance(channel_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_channel(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_channel."""
        stats = StatsGatherer(self.logger)
        channel_stat = stats.quietest_channel(guild_id, self.start, self.end)
        assert isinstance(channel_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_thread(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_thread."""
        stats = StatsGatherer(self.logger)
        thread_stat = stats.busiest_thread(guild_id, self.start, self.end)
        assert isinstance(thread_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_thread(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_thread."""
        stats = StatsGatherer(self.logger)
        thread_stat = stats.quietest_thread(guild_id, self.start, self.end)
        assert isinstance(thread_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_day(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_day."""
        stats = StatsGatherer(self.logger)
        day_stat = stats.busiest_day(guild_id, self.start, self.end)
        assert isinstance(day_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_day(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_day."""
        stats = StatsGatherer(self.logger)
        day_stat = stats.quietest_day(guild_id, self.start, self.end)
        assert isinstance(day_stat, StatDB)

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_bets(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_bets."""
        stats = StatsGatherer(self.logger)
        bet_stat = stats.number_of_bets(guild_id, self.start, self.end)
        assert isinstance(bet_stat, StatDB)
