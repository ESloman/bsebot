"""Tests the StatsDataCache class."""

import datetime
import random
from unittest import mock

import pytest
import pytz

from discordbot.stats.statsdatacache import StatsDataCache
from mongo import interface
from tests.mocks import interface_mocks

INTERACTION_CACHE: list[dict[str, any]] | None = None


def _get_interaction_data(number: int | None = None) -> list[dict[str, any]]:
    """Function for getting and caching internal data."""
    global INTERACTION_CACHE  # noqa: PLW0603
    if INTERACTION_CACHE is None:
        INTERACTION_CACHE = list(interface_mocks.query_mock("userinteractions", {}))
    if not number:
        return INTERACTION_CACHE
    return random.choices(INTERACTION_CACHE, k=number)


class TestStatsDataCache:
    """Tests our StatsDataCache class."""

    def test_stats_data_cache_init(self) -> None:
        """Tests StatsDataCache init."""
        cache = StatsDataCache()
        assert isinstance(cache, StatsDataCache)
        assert not cache.annual
        assert cache._user_id_cache is None

    def test_stats_data_cache_init_with_non_defaults(self) -> None:
        """Tests StatsDataCache init with non-defaults."""
        cache = StatsDataCache(True, 123456)
        assert isinstance(cache, StatsDataCache)
        assert cache.annual
        assert cache._user_id_cache == 123456

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_messages(self, guild_id: int) -> None:
        """Tests StatsDataCache get_messages."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        messages = cache.get_messages(guild_id, start, end)
        assert isinstance(messages, list)
        assert len(messages) > 0

        # test that we set all this correctly
        assert cache._message_cache is not None
        assert cache._message_cache is messages
        assert cache._start_cache == start
        assert cache._end_cache == end

        messages_again = cache.get_messages(guild_id, start, end)
        assert isinstance(messages_again, list)
        # should be the same as above
        assert messages_again is cache._message_cache
        assert messages_again is messages

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_edited_messages(self, guild_id: int) -> None:
        """Tests StatsDataCache get_edited_messages."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        messages = cache.get_edited_messages(guild_id, start, end)
        assert isinstance(messages, list)
        assert len(messages) > 0

        # test that we set all this correctly
        assert cache._edit_cache is not None
        assert cache._edit_cache is messages
        assert cache._start_cache == start
        assert cache._end_cache == end

        messages_again = cache.get_edited_messages(guild_id, start, end)
        assert isinstance(messages_again, list)
        # should be the same as above
        assert messages_again is cache._edit_cache
        assert messages_again is messages

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_vc_interactions(self, guild_id: int) -> None:
        """Tests StatsDataCache get_vc_interactions."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        vcs = cache.get_vc_interactions(guild_id, start, end)
        assert isinstance(vcs, list)
        assert len(vcs) > 0

        # test that we set all this correctly
        assert cache._vc_cache is not None
        assert cache._vc_cache is vcs
        assert cache._start_cache == start
        assert cache._end_cache == end

        vcs_again = cache.get_vc_interactions(guild_id, start, end)
        assert isinstance(vcs_again, list)
        # should be the same as above
        assert vcs_again is cache._vc_cache
        assert vcs_again is vcs

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_bets(self, guild_id: int) -> None:
        """Tests StatsDataCache get_bets."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        bets = cache.get_bets(guild_id, start, end)
        assert isinstance(bets, list)
        assert len(bets) > 0

        # test that we set all this correctly
        assert cache._bet_cache is not None
        assert cache._bet_cache is bets
        assert cache._start_cache == start
        assert cache._end_cache == end

        bets_again = cache.get_bets(guild_id, start, end)
        assert isinstance(bets_again, list)
        # should be the same as above
        assert bets_again is cache._bet_cache
        assert bets_again is bets

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_users(self, guild_id: int) -> None:
        """Tests StatsDataCache get_users."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        users = cache.get_users(guild_id, start, end)
        assert isinstance(users, list)
        assert len(users) > 0

        # test that we set all this correctly
        assert cache._user_cache is not None
        assert cache._user_cache is users
        assert cache._start_cache == start
        assert cache._end_cache == end

        users_again = cache.get_users(guild_id, start, end)
        assert isinstance(users_again, list)
        # should be the same as above
        assert users_again is cache._user_cache
        assert users_again is users

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_transactions(self, guild_id: int) -> None:
        """Tests StatsDataCache get_transactions."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        transactions = cache.get_transactions(guild_id, start, end)
        assert isinstance(transactions, list)
        assert len(transactions) > 0

        # test that we set all this correctly
        assert cache._transaction_cache is not None
        assert cache._transaction_cache is transactions
        assert cache._start_cache == start
        assert cache._end_cache == end

        transactions_again = cache.get_transactions(guild_id, start, end)
        assert isinstance(transactions_again, list)
        # should be the same as above
        assert transactions_again is cache._transaction_cache
        assert transactions_again is transactions

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_activities(self, guild_id: int) -> None:
        """Tests StatsDataCache get_activities."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        activities = cache.get_activities(guild_id, start, end)
        assert isinstance(activities, list)
        assert len(activities) > 0

        # test that we set all this correctly
        assert cache._activity_cache is not None
        assert cache._activity_cache is activities
        assert cache._start_cache == start
        assert cache._end_cache == end

        activities_again = cache.get_activities(guild_id, start, end)
        assert isinstance(activities_again, list)
        # should be the same as above
        assert activities_again is cache._activity_cache
        assert activities_again is activities

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_emojis(self, guild_id: int) -> None:
        """Tests StatsDataCache get_emojis."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        emojis = cache.get_emojis(guild_id, start, end)
        assert isinstance(emojis, list)
        assert len(emojis) > 0

        # test that we set all this correctly
        assert cache._emoji_cache is not None
        assert cache._emoji_cache is emojis
        assert cache._start_cache == start
        assert cache._end_cache == end

        emojis_again = cache.get_emojis(guild_id, start, end)
        assert isinstance(emojis_again, list)
        # should be the same as above
        assert emojis_again is cache._emoji_cache
        assert emojis_again is emojis

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_threaded_messages(self, guild_id: int) -> None:
        """Tests StatsDataCache get_threaded_messages."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        threaded_messages = cache.get_threaded_messages(guild_id, start, end)
        assert isinstance(threaded_messages, list)
        assert len(threaded_messages) > 0

        # test that we set all this correctly
        assert cache._start_cache == start
        assert cache._end_cache == end

        threaded_messages_again = cache.get_threaded_messages(guild_id, start, end)
        assert isinstance(threaded_messages_again, list)
        # should be the same as above
        assert threaded_messages == threaded_messages_again

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_reactions(self, guild_id: int) -> None:
        """Tests StatsDataCache get_reactions."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        reactions = cache.get_reactions(guild_id, start, end)
        assert isinstance(reactions, list)

        # test that we set all this correctly
        assert cache._reactions_cache is not None
        assert cache._reactions_cache is reactions
        assert cache._start_cache == start
        assert cache._end_cache == end

        reactions_again = cache.get_reactions(guild_id, start, end)
        assert isinstance(reactions_again, list)
        # should be the same as above
        assert reactions_again is cache._reactions_cache
        assert reactions_again == reactions

    @pytest.mark.parametrize("guild_id", {entry["guild_id"] for entry in _get_interaction_data(200)})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_stats_data_cache_get_replies(self, guild_id: int) -> None:
        """Tests StatsDataCache get_replies."""
        cache = StatsDataCache()
        now = datetime.datetime.now(tz=pytz.utc)
        start = now.replace(year=2023, month=12, day=1, hour=0, minute=1)
        end = start.replace(year=2024, month=1)
        replies = cache.get_replies(guild_id, start, end)
        assert isinstance(replies, list)
        assert len(replies) > 0

        # test that we set all this correctly
        assert cache._reply_cache is not None
        assert cache._reply_cache is replies
        assert cache._start_cache == start
        assert cache._end_cache == end

        replies_again = cache.get_replies(guild_id, start, end)
        assert isinstance(replies_again, list)
        # should be the same as above
        assert replies_again is cache._reply_cache
        assert replies_again is replies
