"""Tests the StatsDataCache class."""

import datetime
from unittest import mock

import pytest
import pytz
from freezegun import freeze_time

from discordbot.stats.statsclasses import StatsGatherer
from discordbot.stats.statsdataclasses import StatDB
from mongo import interface
from mongo.bsedataclasses import Awards
from tests.mocks import discord_mocks, interface_mocks

AWARD_CACHE: list[dict[str, any]] | None = None


def _get_award_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global AWARD_CACHE  # noqa: PLW0603
    if AWARD_CACHE is None:
        AWARD_CACHE = list(interface_mocks.query_mock("awards", {}))
    if not number:
        return AWARD_CACHE
    return AWARD_CACHE[-number:]


class TestsStatsGatherer:
    """Tests our StatsGatherer class."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""

    def test_stats_gatherer_init_defaults(self) -> None:
        """Tests StatsGatherer init."""
        stats = StatsGatherer()
        assert isinstance(stats, StatsGatherer)
        assert not stats.annual

    def test_stats_gatherer_init_non_defaults(self) -> None:
        """Tests StatsGatherer init."""
        stats = StatsGatherer(True)
        assert isinstance(stats, StatsGatherer)
        assert stats.annual

    @freeze_time("2024-01-01")
    def test_stats_get_monthly_datetime(self) -> None:
        """Tests StatsGatherer get_monthly_datetime_objects."""
        stats = StatsGatherer()
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
        stats = StatsGatherer(True)
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
        stats = StatsGatherer()
        start, _ = stats.get_monthly_datetime_objects()
        new_entry = stats.add_annual_changes(start, entry)
        # shouldn't be changed
        assert new_entry is entry
        assert not new_entry.annual

        annual_stats = StatsGatherer(True)
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
        now = datetime.datetime.now(tz=pytz.utc)
        self.start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        self.end = self.start.replace(year=2024, month=1)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_messages(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_messages."""
        stats = StatsGatherer()
        stat = stats.number_of_messages(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_threaded_messages(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_threaded_messages."""
        stats = StatsGatherer()
        stat = stats.number_of_threaded_messages(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_average_message_length(self, guild_id: int) -> None:
        """Tests StatsGatherer average_message_length."""
        stats = StatsGatherer()
        character_stats, word_stats = stats.average_message_length(guild_id, self.start, self.end)
        assert isinstance(character_stats, StatDB)
        assert isinstance(word_stats, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_channel(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_channel."""
        stats = StatsGatherer()
        stat = stats.busiest_channel(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_channel(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_channel."""
        stats = StatsGatherer()
        stat = stats.quietest_channel(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_thread(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_thread."""
        stats = StatsGatherer()
        stat = stats.busiest_thread(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_thread(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_thread."""
        stats = StatsGatherer()
        stat = stats.quietest_thread(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_busiest_day(self, guild_id: int) -> None:
        """Tests StatsGatherer busiest_day."""
        stats = StatsGatherer()
        stat = stats.busiest_day(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_quiestest_day(self, guild_id: int) -> None:
        """Tests StatsGatherer quiestest_day."""
        stats = StatsGatherer()
        stat = stats.quietest_day(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_number_of_bets(self, guild_id: int) -> None:
        """Tests StatsGatherer number_of_bets."""
        stats = StatsGatherer()
        stat = stats.number_of_bets(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_salary_gains(self, guild_id: int) -> None:
        """Tests StatsGatherer salary_gains."""
        stats = StatsGatherer()
        stat = stats.salary_gains(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_average_wordle_victory(self, guild_id: int) -> None:
        """Tests StatsGatherer average_wordle_victory."""
        stats = StatsGatherer()
        stat = stats.average_wordle_victory(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_bet_eddies(self, guild_id: int) -> None:
        """Tests StatsGatherer bet_eddies_stats."""
        stats = StatsGatherer()
        placed_stat, won_stat = stats.bet_eddies_stats(guild_id, self.start, self.end)
        assert isinstance(placed_stat, StatDB)
        assert isinstance(won_stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_unique_contributors(self, guild_id: int) -> None:
        """Tests StatsGatherer most_unique_channel_contributers."""
        stats = StatsGatherer()
        stat = stats.most_unique_channel_contributers(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_total_time_spent_in_vc(self, guild_id: int) -> None:
        """Tests StatsGatherer total_time_spent_in_vc."""
        stats = StatsGatherer()
        stat = stats.total_time_spent_in_vc(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_vc_with_most_time_spent(self, guild_id: int) -> None:
        """Tests StatsGatherer vc_with_most_time_spent."""
        stats = StatsGatherer()
        stat = stats.vc_with_most_time_spent(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_vc_with_most_users(self, guild_id: int) -> None:
        """Tests StatsGatherer vc_with_most_users."""
        stats = StatsGatherer()
        stat = stats.vc_with_most_users(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_popular_server_emoji(self, guild_id: int) -> None:
        """Tests StatsGatherer most_popular_server_emoji."""
        stats = StatsGatherer()
        stat = stats.most_popular_server_emoji(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_threads_created(self, guild_id: int) -> None:
        """Tests StatsGatherer threads_created."""
        stats = StatsGatherer()
        stat = stats.threads_created(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_emojis_created(self, guild_id: int) -> None:
        """Tests StatsGatherer emojis_created."""
        stats = StatsGatherer()
        stat = stats.emojis_created(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)


class TestsStatsGathererAwardsMethods:  # noqa: PLR0904
    """Tests our StatsGatherer class and it's actual awards methods."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.guild = discord_mocks.GuildMock(123456)

        now = datetime.datetime.now(tz=pytz.utc)
        self.start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        self.end = self.start.replace(year=2024, month=1)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_server_owner(self) -> None:
        """Tests StatsGatherer server_owner award."""
        stats = StatsGatherer()
        stat = stats.server_owner(self.guild, self.start)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_messages_sent(self, guild_id: int) -> None:
        """Tests StatsGatherer most_messages_sent award."""
        stats = StatsGatherer()
        stat = stats.most_messages_sent(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_least_messages_sent(self, guild_id: int) -> None:
        """Tests StatsGatherer least_messages_sent award."""
        stats = StatsGatherer()
        stat = stats.least_messages_sent(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_thread_messages_sent(self, guild_id: int) -> None:
        """Tests StatsGatherer most_thread_messages_sent award."""
        stats = StatsGatherer()
        stat = stats.most_thread_messages_sent(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_longest_message(self, guild_id: int) -> None:
        """Tests StatsGatherer longest_message award."""
        stats = StatsGatherer()
        stat = stats.longest_message(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_alphabetical(self, guild_id: int) -> None:
        """Tests StatsGatherer most_alphabetical_messages award."""
        stats = StatsGatherer()
        stat = stats.most_alphabetical_messages(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_lowest_average_wordle_score(self, guild_id: int) -> None:
        """Tests StatsGatherer lowest_average_wordle_score award."""
        stats = StatsGatherer()
        stat = stats.lowest_average_wordle_score(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_highest_average_wordle_score(self, guild_id: int) -> None:
        """Tests StatsGatherer highest_average_wordle_score award."""
        stats = StatsGatherer()
        stat = stats.highest_average_wordle_score(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_wordle_most_greens(self, guild_id: int) -> None:
        """Tests StatsGatherer wordle_most_greens award."""
        stats = StatsGatherer()
        stat = stats.wordle_most_greens(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_wordle_most_yellows(self, guild_id: int) -> None:
        """Tests StatsGatherer wordle_most_yellows award."""
        stats = StatsGatherer()
        stat = stats.wordle_most_yellows(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_wordle_most_symmetry(self, guild_id: int) -> None:
        """Tests StatsGatherer wordle_most_symmetry award."""
        stats = StatsGatherer()
        stat = stats.wordle_most_symmetry(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_twitter_addict(self, guild_id: int) -> None:
        """Tests StatsGatherer twitter_addict award."""
        stats = StatsGatherer()
        stat = stats.twitter_addict(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_jerk_off_contributor(self, guild_id: int) -> None:
        """Tests StatsGatherer jerk_off_contributor award."""
        stats = StatsGatherer()
        stat = stats.jerk_off_contributor(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_big_memer(self, guild_id: int) -> None:
        """Tests StatsGatherer big_memer award."""
        stats = StatsGatherer()
        stat = stats.big_memer(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_react_king(self, guild_id: int) -> None:
        """Tests StatsGatherer react_king award."""
        stats = StatsGatherer()
        stat = stats.react_king(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_replies(self, guild_id: int) -> None:
        """Tests StatsGatherer most_replies award."""
        stats = StatsGatherer()
        most_replied_to_stat, most_replies_stat = stats.most_replies(guild_id, self.start, self.end)
        assert isinstance(most_replies_stat, StatDB)
        assert isinstance(most_replied_to_stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_edited_messages(self, guild_id: int) -> None:
        """Tests StatsGatherer most_edited_messages award."""
        stats = StatsGatherer()
        stat = stats.most_edited_messages(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_swears(self, guild_id: int) -> None:
        """Tests StatsGatherer most_swears award."""
        stats = StatsGatherer()
        stat = stats.most_swears(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_messages_to_a_single_channel(self, guild_id: int) -> None:
        """Tests StatsGatherer most_messages_to_a_single_channel award."""
        stats = StatsGatherer()
        stat = stats.most_messages_to_a_single_channel(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_messages_to_most_channels(self, guild_id: int) -> None:
        """Tests StatsGatherer most_messages_to_most_channels award."""
        stats = StatsGatherer()
        stat = stats.most_messages_to_most_channels(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_bets_created(self, guild_id: int) -> None:
        """Tests StatsGatherer most_bets_created award."""
        stats = StatsGatherer()
        stat = stats.most_bets_created(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_eddies_bet(self, guild_id: int) -> None:
        """Tests StatsGatherer most_eddies_bet award."""
        stats = StatsGatherer()
        stat = stats.most_eddies_bet(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_eddies_won(self, guild_id: int) -> None:
        """Tests StatsGatherer most_eddies_won award."""
        stats = StatsGatherer()
        stat = stats.most_eddies_won(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_most_time_king(self, guild_id: int) -> None:
        """Tests StatsGatherer most_time_king award."""
        stats = StatsGatherer()
        stat = stats.most_time_king(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_big_gamer(self, guild_id: int) -> None:
        """Tests StatsGatherer big_gamer award."""
        stats = StatsGatherer()
        stat = stats.big_gamer(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_big_streamer(self, guild_id: int) -> None:
        """Tests StatsGatherer big_streamer award."""
        stats = StatsGatherer()
        stat = stats.big_streamer(guild_id, self.start, self.end)
        assert isinstance(stat, StatDB)
