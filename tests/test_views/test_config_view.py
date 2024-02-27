"""Tests our config views."""

from unittest import mock

import pytest

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.bseview import BSEView
from discordbot.views.config import ConfigView
from discordbot.views.config_admin import AdminConfigView
from discordbot.views.config_autogenerate import AutoGenerateConfigView
from discordbot.views.config_bseddies import BSEddiesConfigView
from discordbot.views.config_revolution import RevolutionConfigView
from discordbot.views.config_salary import SalaryConfigView
from discordbot.views.config_salary_message import DailyMessageView
from discordbot.views.config_threads import ThreadConfigView
from discordbot.views.config_valorant import ValorantConfigView
from discordbot.views.config_wordle import WordleRootConfigView
from mongo import interface
from tests.mocks import discord_mocks, interface_mocks


class TestConfigView:
    """Tests our ConfigView view."""

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(PlaceHolderLogger)

    async def test_cancel_callback(self) -> None:
        """Tests cancel callback."""
        view = ConfigView(PlaceHolderLogger)
        interaction = discord_mocks.InteractionMock(123456)
        await view.cancel_callback(None, interaction)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init_with_user_id_not_guild_id(self, user_data: dict[str, any]) -> None:
        """Tests basic init with user_id and not guild id.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(PlaceHolderLogger, user_data["uid"])

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init_with_values(self, guild_data: dict[str, any], user_data: dict[str, any]) -> None:
        """Tests basic init with guild and user data.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(PlaceHolderLogger, user_data["uid"], guild_data["guild_id"])

    async def test_send_no_perms_message(self) -> None:
        """Tests send no perms message.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        config = ConfigView(PlaceHolderLogger)
        interaction = discord_mocks.InteractionMock(123456)
        await config._send_no_perms_message(interaction)

    @pytest.mark.parametrize("value", ["daily_salary", "activities", "wordle_starting_words", "something"])
    @pytest.mark.parametrize("user_data", [*interface_mocks.query_mock("userpoints", {})[-5:], {"uid": CREATOR}])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_perms(self, value: str, user_data: dict[str, any]) -> None:
        """Tests check perms with basic values and some users.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        config = ConfigView(PlaceHolderLogger, user_data["uid"])
        config._check_perms(value, user_data["uid"])

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_thread_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_thread_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_thread_message_and_view(interaction)
        assert "## Thread Configuration" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, ThreadConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_valorant_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_valorant_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_valorant_message_and_view(interaction)
        assert "## Valorant Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, ValorantConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_daily_minimum_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_daily_minimum_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_daily_minimum_message_and_view(interaction)
        assert "## Salary Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, SalaryConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_admins_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_admins_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_admins_message_and_view(interaction)
        assert "## Admins Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, AdminConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_revolution_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_revolution_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_revolution_message_and_view(interaction)
        assert "## Revolution Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, RevolutionConfigView)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_daily_salary_message_and_view(self, user_data: dict[str, any]) -> None:
        """Tests _get_daily_salary_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(user_data["guild_id"], user_data["uid"])

        msg, view = config._get_daily_salary_message_and_view(interaction)
        assert "## Daily Salary Message" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, DailyMessageView)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_daily_salary_message_and_view_guildless(self, user_data: dict[str, any]) -> None:
        """Tests _get_daily_salary_message_and_view method with no guild data."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(user_data["guild_id"], user_data["uid"])
        interaction.guild = None

        msg, view = config._get_daily_salary_message_and_view(interaction)
        assert "## Daily Salary Message" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, DailyMessageView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_bseddies_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_bseddies_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_bseddies_message_and_view(interaction)
        assert "## BSEddies Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, BSEddiesConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_autogenerate_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_autogenerate_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_autogenerate_message_and_view(interaction)
        assert "## Autogenerate Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, AutoGenerateConfigView)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_get_wordle_message_and_view(self, guild_data: dict[str, any]) -> None:
        """Tests _get_wordle_message_and_view method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(guild_data["guild_id"], CREATOR)

        msg, view = config._get_wordle_message_and_view(interaction)
        assert "## Wordle Config" in msg
        assert isinstance(view, BSEView)
        assert isinstance(view, WordleRootConfigView)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-10:])
    @pytest.mark.parametrize("value", {value[1] for value in ConfigSelect._values})
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_place_callback(self, user_data: dict[str, any], value: str) -> None:
        """Tests place_callback method."""
        config = ConfigView(PlaceHolderLogger, CREATOR)
        interaction = discord_mocks.InteractionMock(user_data["guild_id"], user_data["uid"])

        interaction.data["values"] = [value]
        config.config_select.refresh_state(interaction)

        await config.place_callback.callback(interaction)
