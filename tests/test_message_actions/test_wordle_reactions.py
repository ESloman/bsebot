"""Tests our WordleReactions message action class."""

import datetime
from unittest import mock

import pytest
from bson import ObjectId

from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_actions.wordle_reactions import WordleMessageAction
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.message import MessageDB
from tests.mocks import message_action_mocks
from tests.mocks.bsebot_mocks import BSEBotMock
from tests.mocks.discord_mocks import MessageMock


class TestWordleReactions:
    """Tests our WordleReactions class."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = BSEBotMock()

        self.message = MessageMock()

    def test_init(self) -> None:
        """Tests init."""
        action = WordleMessageAction(self.client)
        assert isinstance(action, BaseMessageAction)

    @pytest.mark.parametrize("message_type", [[], ["message", "link"], ["message", "wordle"]])
    async def test_pre_condition(self, message_type: list[str]) -> None:
        """Tests the pre_condition function."""
        action = WordleMessageAction(self.client)
        expected = "wordle" in message_type
        assert await action.pre_condition(self.message, message_type) == expected

    @pytest.mark.parametrize(("content", "exp"), message_action_mocks.get_wordle_squares_content())
    async def test_adding_squares(self, content: str, exp: str | None) -> None:
        """Tests the handle_adding_squares function."""
        action = WordleMessageAction(self.client)
        message = MessageMock(content)
        with mock.patch.object(message, "add_reaction") as patched:
            await action._handle_adding_squares(message)
            assert patched.called == (exp is not None)
            if exp is not None:
                patched.assert_called_once_with(exp)

    @pytest.mark.parametrize(("content", "exp"), message_action_mocks.get_wordle_symmetry_content())
    async def test_handle_symmetry(self, content: str, exp: bool) -> None:
        """Tests the handle_symmetry function."""
        action = WordleMessageAction(self.client)
        message = MessageMock(content)
        with mock.patch.object(message, "add_reaction") as patched:
            await action._handle_symmetry(message)
            assert patched.called is exp

    @pytest.mark.parametrize(
        ("return_val", "exp_called"),
        [
            ([{"content": "6/6"} for _ in range(4)], True),
            ([{"content": f"{x}/6"} for x in range(6)], False),
            ([{"content": "6/6"} for _ in range(4)] + [{"content": "https://imgur.com/Uk73HPD"}], False),
        ],
    )
    async def test_tough_day_status(self, return_val: list[dict[str, str]], exp_called: bool) -> None:
        """Tests the tough_day_status function."""
        action = WordleMessageAction(self.client)
        message = MessageMock("")
        messages = [
            MessageDB(
                message.channel_id,
                message.message_id,
                ObjectId(),
                message.guild.id,
                message.user_id,
                datetime.datetime.now(),
                mess["content"],
                ["message", "wordle"],
            )
            for mess in return_val
        ]
        with (
            mock.patch.object(action.user_interactions, "query", return_value=messages),
            mock.patch.object(message.channel, "send") as send_patch,
        ):
            await action._handle_tough_day_status(message)
            assert send_patch.called is exp_called

    @pytest.mark.parametrize(
        "func", [message_action_mocks.query_tough_day_exc, message_action_mocks.query_tough_day_exc_sec]
    )
    async def test_tough_day_status_error(self, func: callable) -> None:
        """Tests the tough_day_status function with Operation error.."""
        action = WordleMessageAction(self.client)
        message = MessageMock("")
        with (
            mock.patch.object(action.user_interactions, "query", new=func),
            mock.patch.object(message.channel, "send") as send_patch,
        ):
            await action._handle_tough_day_status(message)
            assert not send_patch.called

    @pytest.mark.parametrize(("content", "exp_reaction"), message_action_mocks.get_wordle_run_content())
    async def test_run(self, content: str, exp_reaction: str | None) -> None:
        """Tests the run function."""
        action = WordleMessageAction(self.client)
        message = MessageMock(content)
        with (
            mock.patch.object(action, "_handle_adding_squares") as squares_patch,
            mock.patch.object(action, "_handle_tough_day_status") as tough_day_patch,
            mock.patch.object(message, "add_reaction") as message_patch,
            mock.patch.object(action.guilds, "get_guild", return_value=GuildDB(ObjectId(), 123, "guild", 456)),
        ):
            await action.run(message)
            assert squares_patch.called
            assert tough_day_patch.called == (exp_reaction is not None)
            if exp_reaction:
                message_patch.assert_called_with(exp_reaction)
