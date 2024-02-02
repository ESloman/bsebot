"""Tests our config views."""

from unittest import mock

import pytest

from discordbot.constants import CREATOR
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.config import ConfigView
from mongo import interface
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestConfigView:
    """Tests our ConfigView view."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Fixture to get test data.

        Automatically called before each test.
        """
        self.bsebot = bsebot_mocks.BSEBotMock()
        self.logger = PlaceHolderLogger

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init(self) -> None:
        """Tests basic init.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(self.bsebot)

    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init_with_user_id_not_guild_id(self, user_data: dict) -> None:
        """Tests basic init with user_id and not guild id.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(self.bsebot, user_data["uid"])

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {})[-5:])
    @pytest.mark.parametrize("user_data", interface_mocks.query_mock("userpoints", {})[-5:])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_init_with_values(self, guild_data: dict, user_data: dict) -> None:
        """Tests basic init with guild and user data.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        _ = ConfigView(self.bsebot, user_data["uid"], guild_data["guild_id"])

    async def test_send_no_perms_message(self) -> None:
        """Tests send no perms message.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        config = ConfigView(self.bsebot)
        interaction = discord_mocks.InteractionMock(123456)
        await config._send_no_perms_message(interaction)

    @pytest.mark.parametrize("value", ["daily_salary", "activities", "wordle_starting_words", "something"])
    @pytest.mark.parametrize("user_data", [*interface_mocks.query_mock("userpoints", {})[-5:], {"uid": CREATOR}])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_check_perms(self, value: str, user_data: dict) -> None:
        """Tests check perms with basic values and some users.

        Needs to run with async as the parent class tries to get the running event loop.
        """
        config = ConfigView(self.bsebot, user_data["uid"])
        config._check_perms(value, user_data["uid"])
