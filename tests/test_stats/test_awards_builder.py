"""Tests the AwardsBuilder class."""

from unittest import mock

import pytest
from freezegun import freeze_time

from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.stats.statsdataclasses import StatDB
from mongo import interface
from tests.mocks import bsebot_mocks, interface_mocks


class TestAwardsBuilderStatics:
    """Tests the Awards Builder static methods."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.client = bsebot_mocks.BSEBotMock()

    @pytest.mark.parametrize(
        ("old", "new", "expected"),
        [
            (100, 120, " (up `20.0%`)"),
            (100, 100, " (no change)"),
            (100, 80, " (down `20.0%`)"),
        ],
    )
    def test_get_comparison_string(self, old: float, new: float, expected: str) -> None:
        """Tests getting the comparison string function."""
        awards_builder = AwardsBuilder(self.client, 123456)
        comp_string = awards_builder._get_comparison_string(new, old)
        assert expected == comp_string


class TestAwardsBuilderStatsAndAwards:
    """Tests the Awards Builder stats and awards methods."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.client = bsebot_mocks.BSEBotMock()

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @freeze_time("2024-01-01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_build_stats_and_message(self, guild_id: int) -> None:
        """Tests our build_stats_and_message function."""
        awards_builder = AwardsBuilder(self.client, guild_id)
        stats, messages = await awards_builder.build_stats_and_message()
        assert isinstance(stats, list)
        assert isinstance(messages, list)
        for stat in stats:
            assert isinstance(stat, StatDB)
        for message in messages:
            assert isinstance(message, str)
            assert len(message) < 2000

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @freeze_time("2024-01-01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_build_stats_and_message_annual(self, guild_id: int) -> None:
        """Tests our build_stats_and_message function in annual mode."""
        awards_builder = AwardsBuilder(self.client, guild_id, True)
        stats, messages = await awards_builder.build_stats_and_message()
        assert isinstance(stats, list)
        assert isinstance(messages, list)
        for stat in stats:
            assert isinstance(stat, StatDB)
        for message in messages:
            assert isinstance(message, str)
            assert len(message) < 2000

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @freeze_time("2024-01-01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_build_awards_and_message(self, guild_id: int) -> None:
        """Tests our build_awards_and_message function."""
        awards_builder = AwardsBuilder(self.client, guild_id)
        stats, messages = await awards_builder.build_awards_and_message()
        assert isinstance(stats, list)
        assert isinstance(messages, list)
        for stat in stats:
            assert isinstance(stat, StatDB)
        for message in messages:
            assert isinstance(message, str)
            assert len(message) < 2000

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @freeze_time("2024-01-01")
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_build_awards_and_message_annual(self, guild_id: int) -> None:
        """Tests our build_awards_and_message function in annual mode."""
        awards_builder = AwardsBuilder(self.client, guild_id, True)
        stats, messages = await awards_builder.build_awards_and_message()
        assert isinstance(stats, list)
        assert isinstance(messages, list)
        for stat in stats:
            assert isinstance(stat, StatDB)
        for message in messages:
            assert isinstance(message, str)
            assert len(message) < 2000
