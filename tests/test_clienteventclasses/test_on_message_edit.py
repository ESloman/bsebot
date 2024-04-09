"""Tests our OnMessageEdit client event class."""

from unittest import mock

import discord
import pytest
from bson import ObjectId

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onmessageedit import OnMessageEdit
from discordbot.constants import BSE_BOT_ID
from mongo import interface
from mongo.datatypes.message import MessageDB
from tests.mocks import bsebot_mocks, discord_mocks, interface_mocks


class TestOnMessageEdit:
    """Tests our OnMessageEdit commands."""

    @pytest.fixture(autouse=True)
    def _data(self) -> None:
        self.client = bsebot_mocks.BSEBotMock()

    def test_init(self) -> None:
        """Tests basic initialisation."""
        event = OnMessageEdit(self.client, [], self.logger)
        assert isinstance(event, OnMessageEdit)
        assert isinstance(event, BaseEvent)

    def test_check_condition_ephemeral(self) -> None:
        """Tests _check_condition with an ephemeral messsage."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock()
        after.flags.ephemeral = True

        assert not event._check_condition(before, after)

    def test_check_condition_application_command(self) -> None:
        """Tests _check_condition with an application command messsage."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock()
        after._type = discord.MessageType.application_command

        assert not event._check_condition(before, after)

    def test_check_condition_bot_embeds(self) -> None:
        """Tests _check_condition with a bot message with embeds."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock(user_id=BSE_BOT_ID)
        after._embeds.append(discord.Embed())

        assert not event._check_condition(before, after)

    @pytest.mark.parametrize(
        "channel_type",
        [
            _type
            for _type in discord.ChannelType
            if _type
            not in {
                discord.ChannelType.text,
                discord.ChannelType.private,
                discord.ChannelType.voice,
                discord.ChannelType.public_thread,
                discord.ChannelType.private_thread,
                discord.ChannelType.news_thread,
            }
        ],
    )
    def test_check_condition_channel_type(self, channel_type: discord.ChannelType) -> None:
        """Tests _check_condition with an invalid channel type."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock()
        after._channel._type = channel_type

        assert not event._check_condition(before, after)

    def test_check_condition_just_embeds(self) -> None:
        """Tests _check_condition with an edit that's just adding an embed."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock()
        after._embeds.append(discord.Embed())

        assert not event._check_condition(before, after)

    def test_check_condition_pass(self) -> None:
        """Tests _check_condition that will pass."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock(content="Test")
        after = discord_mocks.MessageMock(content="Test 2")
        assert event._check_condition(before, after)

    async def test_message_edit_condition_fail(self) -> None:
        """Tests message_edit event with the condition failing."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock()
        after = discord_mocks.MessageMock()
        after.flags.ephemeral = True
        await event.message_edit(before, after)

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.object(interface, "update", new=interface_mocks.update_mock)
    async def test_message_edit(self) -> None:
        """Tests message_edit event."""
        event = OnMessageEdit(self.client, [], self.logger)
        before = discord_mocks.MessageMock(content="Test")
        after = discord_mocks.MessageMock(content="Test 2")

        message_db = MessageDB(
            after.channel_id,
            after.message_id,
            ObjectId(),
            after.guild.id,
            after.user_id,
            after.created_at,
            after.content,
            ["message"],
        )

        with mock.patch.object(event.interactions, "get_message", return_val=message_db):
            await event.message_edit(before, after)
