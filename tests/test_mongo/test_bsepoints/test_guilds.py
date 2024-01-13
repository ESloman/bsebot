"""Tests our Guilds class."""

import datetime
from unittest import mock

import pytest

from mongo import interface
from mongo.bsepoints.guilds import Guilds
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.user import UserDB
from tests.mocks import interface_mocks


class TestGuilds:  # noqa: PLR0904
    """Tests our Guilds class."""

    def test_guilds_init(self) -> None:
        """Tests Guilds init."""
        guilds = Guilds()
        assert isinstance(guilds, Guilds)
        assert guilds.database is not None
        assert guilds.vault is not None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_guild(self, guild_id: int) -> None:
        """Tests Guilds get_guild method."""
        guilds = Guilds()
        guild = guilds.get_guild(guild_id)
        assert isinstance(guild, GuildDB)
        assert guild.guild_id == guild_id

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_guild_none(self) -> None:
        """Tests Guilds get_guild method."""
        guilds = Guilds()
        guild = guilds.get_guild(123456)
        assert guild is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    def test_guilds_insert_guild(self, guild_id: int) -> None:
        """Tests Guilds insert_guild method."""
        guilds = Guilds()
        guilds.insert_guild(guild_id, "name", 123456, datetime.datetime.now())

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_channel(self, guild_id: int) -> None:
        """Tests Guilds get_channel method."""
        guilds = Guilds()
        channel = guilds.get_channel(guild_id)
        assert channel is not None
        assert isinstance(channel, int)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_channel_none(self) -> None:
        """Tests Guilds get_channel method return None as expected."""
        guilds = Guilds()
        channel = guilds.get_channel(123456)
        assert channel is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king(self, guild_id: int) -> None:
        """Tests Guilds get_king method."""
        guilds = Guilds()
        king = guilds.get_king(guild_id)
        assert king is not None
        assert isinstance(king, int)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king_whole_class(self, guild_id: int) -> None:
        """Tests Guilds get_king method and return the whole class."""
        guilds = Guilds()
        king = guilds.get_king(guild_id, True)
        assert king is not None
        assert isinstance(king, UserDB)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_king_none(self) -> None:
        """Tests Guilds get_king method return None as expected."""
        guilds = Guilds()
        king = guilds.get_king(123456)
        assert king is None

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_king(self, guild_id: int) -> None:
        """Tests Guilds set_king method."""
        guilds = Guilds()
        with mock.patch.object(guilds, "update") as update_patched:
            guilds.set_king(guild_id, 123456)
            assert update_patched.called
            assert len(update_patched.call_args) == 2

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_add_pledger(self) -> None:
        """Tests Guilds add_pledger."""
        guilds = Guilds()
        guilds.add_pledger(123456, 654321)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_reset_pledges(self) -> None:
        """Tests Guilds reset_pledges."""
        guilds = Guilds()
        guilds.reset_pledges(123456)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_revolution_toggle(self) -> None:
        """Tests Guilds set_revolution_toggle."""
        guilds = Guilds()
        guilds.set_revolution_toggle(123456, False)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_daily_minimum(self, guild_id: int) -> None:
        """Tests Guilds get_daily_minimum."""
        guilds = Guilds()
        minimum = guilds.get_daily_minimum(guild_id)
        assert isinstance(minimum, int)
        assert minimum > 0

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_daily_minimum_none(self) -> None:
        """Tests Guilds get_daily_minimum is None when guild isn't found."""
        guilds = Guilds()
        minimum = guilds.get_daily_minimum(123456)
        assert minimum is None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_daily_minimum(self) -> None:
        """Tests Guilds set_daily_minimum."""
        guilds = Guilds()
        guilds.set_daily_minimum(123456, 4)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_update_tax_history(self) -> None:
        """Tests Guilds update_tax_history."""
        guilds = Guilds()
        guilds.update_tax_history(123456, 0.5, 0.1, 654321)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_tax_rate(self) -> None:
        """Tests Guilds set_tax_rate."""
        guilds = Guilds()
        guilds.set_tax_rate(123456, 0.5, 0.1)

    @pytest.mark.parametrize(
        "guild_id",
        # load list of entries dynamically
        {entry["guild_id"] for entry in interface_mocks.query_mock("guilds", {})},
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_tax_rate(self, guild_id: int) -> None:
        """Tests Guilds get_tax_rate."""
        guilds = Guilds()
        tax_rate, supporter_rate = guilds.get_tax_rate(guild_id)
        assert isinstance(tax_rate, float | int)
        assert isinstance(supporter_rate, float | int)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_get_tax_rate_not_set(self) -> None:
        """Tests Guilds get_tax_rate when not set."""
        guilds = Guilds()
        tax_rate, supporter_rate = guilds.get_tax_rate(123456)
        assert isinstance(tax_rate, float | int)
        assert isinstance(supporter_rate, float | int)
        assert tax_rate == 0.1
        assert supporter_rate == 0

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_last_ad_time_none(self) -> None:
        """Tests Guilds get_last_ad_time."""
        guilds = Guilds()
        _time = guilds.get_last_ad_time(123456)
        assert _time is None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_last_ad_time(self) -> None:
        """Tests Guilds get_last_ad_time."""
        guilds = Guilds()
        _time = guilds.get_last_ad_time(724395292912255056)
        assert _time is not None
        assert isinstance(_time, datetime.datetime)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_last_ad_time(self) -> None:
        """Tests Guilds set_last_ad_time."""
        guilds = Guilds()
        guilds.set_last_ad_time(123456, datetime.datetime.now())

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_last_remind_me_time_none(self) -> None:
        """Tests Guilds get_last_remind_me_time."""
        guilds = Guilds()
        _time = guilds.get_last_remind_me_time(123456)
        assert _time is None

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_guilds_get_last_remind_me_time(self) -> None:
        """Tests Guilds get_last_remind_me_time."""
        guilds = Guilds()
        _time = guilds.get_last_remind_me_time(724395292912255056)
        assert _time is not None
        assert isinstance(_time, datetime.datetime)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_last_remind_me_time(self) -> None:
        """Tests Guilds set_last_remind_me_time."""
        guilds = Guilds()
        guilds.set_last_remind_me_time(123456, datetime.datetime.now())

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_valorant_config(self) -> None:
        """Tests Guilds set_valorant_config."""
        guilds = Guilds()
        guilds.set_valorant_config(123456, False)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    def test_guilds_set_wordle_config(self) -> None:
        """Tests Guilds set_wordle_config."""
        guilds = Guilds()
        guilds.set_wordle_config(123456, False)
