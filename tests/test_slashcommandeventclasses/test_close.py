"""Tests our Active Slash Command class."""

from unittest import mock

import pytest

from discordbot.bot_enums import ActivityTypes
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import CloseBet
from mongo import interface
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.guilds import Guilds
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestClose:
    """Tests our Close commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()
        self.guild_ids = [123456, 65321]

    def test_init(self) -> None:
        """Tests basic initialisation."""
        close = CloseBet(self.client, self.guild_ids)
        assert isinstance(close, CloseBet)
        assert isinstance(close, BSEddies)
        assert isinstance(close, BaseEvent)
        assert close.activity_type == ActivityTypes.BSEDDIES_BET_CLOSE
        assert close.help_string is not None

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {}))
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_create_bet_view(self, guild_data: dict) -> None:
        """Tests create_bet_view with no bets."""
        close = CloseBet(self.client, self.guild_ids)

        guild = Guilds.make_data_class(guild_data)
        _users = interface_mocks.query_mock("userpoints", {"guild_id": guild.guild_id})
        for user in _users:
            _bets = interface_mocks.query_mock("userbets", {"guild_id": guild.guild_id, "user_id": user["uid"]})
            if _bets:
                break
        ctx = discord_mocks.ContextMock(guild.guild_id, user["uid"])
        await close.create_bet_view(ctx)

    @pytest.mark.parametrize("guild_data", interface_mocks.query_mock("guilds", {}))
    @pytest.mark.parametrize("number", [10, 30])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    async def test_create_bet_view_with_bets(self, guild_data: dict, number: int) -> None:
        """Tests create_bet_view with bets."""
        close = CloseBet(self.client, self.guild_ids)

        guild = Guilds.make_data_class(guild_data)
        _bets = [b for b in interface_mocks.query_mock("userbets", {"guild_id": guild.guild_id}) if "type" not in b][
            -number:
        ]
        ctx = discord_mocks.ContextMock(guild.guild_id, _bets[0]["user"])
        await close.create_bet_view(
            ctx, [UserBets.make_data_class(b) for b in _bets if b["user"] == _bets[0].get("user")]
        )

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_close_bet_bad_id(self) -> None:
        """Tests close bet with a bad bet ID."""
        close = CloseBet(self.client, self.guild_ids)

        interaction = discord_mocks.InteractionMock(123456)
        await close.close_bet(interaction, "0123", [":one:"])

    @pytest.mark.parametrize(
        "bet_data",
        [
            b
            for b in interface_mocks.query_mock("userbets", {"active": False})
            if "type" not in b and not b.get("result")
        ][-10:],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_close_bet_bad_bets(self, bet_data: dict) -> None:
        """Tests close_bet with bad bets."""
        close = CloseBet(self.client, self.guild_ids)
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        await close.close_bet(interaction, bet.bet_id, bet.options)

    @pytest.mark.parametrize(
        "bet_data", [b for b in interface_mocks.query_mock("userbets", {"active": False}) if "type" not in b][-15:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_close_bet(self, bet_data: dict) -> None:
        """Tests close_bet."""
        close = CloseBet(self.client, self.guild_ids)
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        await close.close_bet(interaction, bet.bet_id, bet.options)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_cancel_bet_bad_id(self) -> None:
        """Tests cancel bet with a bad bet ID."""
        close = CloseBet(self.client, self.guild_ids)

        interaction = discord_mocks.InteractionMock(123456)
        await close.cancel_bet(interaction, "0123")

    @pytest.mark.parametrize(
        "bet_data",
        [
            b
            for b in interface_mocks.query_mock("userbets", {"active": False})
            if "type" not in b and not b.get("result")
        ][-10:],
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_cancel_bet_bad_bets(self, bet_data: dict) -> None:
        """Tests cancel_bet with bad bets."""
        close = CloseBet(self.client, self.guild_ids)
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        await close.cancel_bet(interaction, bet.bet_id)

    @pytest.mark.parametrize(
        "bet_data", [b for b in interface_mocks.query_mock("userbets", {"active": False}) if "type" not in b][-15:]
    )
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    @mock.patch.object(interface, "insert", new=interface_mocks.insert_mock)
    async def test_cancel_bet(self, bet_data: dict) -> None:
        """Tests cancel_bet."""
        close = CloseBet(self.client, self.guild_ids)
        bet = UserBets.make_data_class(bet_data)
        interaction = discord_mocks.InteractionMock(bet.guild_id, bet.user)
        await close.cancel_bet(interaction, bet.bet_id)
