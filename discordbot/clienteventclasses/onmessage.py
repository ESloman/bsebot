"""Contains our OnMessage class.

Handles on_message events.
"""

import contextlib
import re
from typing import TYPE_CHECKING

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import WORDLE_REGEX

# message actions
from discordbot.message_actions.alphabetical_reactions import AlphabeticalMessageAction
from discordbot.message_actions.birthday_replies import BirthdayReplies
from discordbot.message_actions.command_suggestion import CommandSuggest
from discordbot.message_actions.duplicate_links import DuplicateLinkAction
from discordbot.message_actions.marvel_ad import MarvelComicsAdAction
from discordbot.message_actions.remind_me import RemindMeAction
from discordbot.message_actions.rigged import RiggedAction
from discordbot.message_actions.thank_you_replies import ThankYouReplies
from discordbot.message_actions.wordle_reactions import WordleMessageAction

if TYPE_CHECKING:
    from discordbot.message_actions.base import BaseMessageAction


class OnMessage(BaseEvent):
    """Class for handling on_message events from Discord."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Sets up our list of post message action classes.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self._post_message_action_classes: list[BaseMessageAction] = [
            AlphabeticalMessageAction(client),
            BirthdayReplies(client),
            CommandSuggest(client),
            DuplicateLinkAction(client),
            MarvelComicsAdAction(client),
            RemindMeAction(client),
            RiggedAction(client),
            ThankYouReplies(client),
            WordleMessageAction(client),
        ]

    @staticmethod
    def _get_ids(message: discord.Message) -> tuple[int, int]:
        """Gets and returns user_id and channel_id.

        Works it out and returns to prevent us passing those around everywhere.

        Args:
            message (discord.Message): the message

        Returns:
            tuple[int, int]: user_id, channel_id
        """
        user_id = message.author.id
        channel_id = message.channel.id
        return user_id, channel_id

    @staticmethod
    def _get_message_flags(message: discord.Message) -> tuple[bool, bool, bool]:
        """Calculates some message flags.

        Works out is_bot, is_thread, and is_vc to prevent us passing those around everywhere.

        Args:
            message (discord.Message): the message

        Returns:
            tuple[bool, bool, bool]: is_bot, is_thread, is_vc
        """
        is_bot = message.author.bot
        is_thread = False
        is_vc = False
        if message.channel.type in {
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread,
        }:
            is_thread = True

        if message.channel.type in {discord.ChannelType.voice, discord.ChannelType.stage_voice}:
            is_vc = True

        return is_bot, is_thread, is_vc

    @staticmethod
    def _handle_attachments(message: discord.Message, message_type: list[str]) -> None:
        """Handles attachments.

        Args:
            message (discord.Message): the message
            message_type (list): message_type list to update
        """
        if not message.attachments:
            return

        for attachment in message.attachments:
            message_type.append("attachment")
            # this is only a temporary fix until https://github.com/Pycord-Development/pycord/pull/2016 is merged
            # and pycord officially supports voice messages
            if attachment.filename == "voice-message.ogg":
                message_type.append("voice_message")

    def _handle_mentions(self, message: discord.Message, message_type: list[str]) -> None:
        """Handles mentions.

        Works out if there were any mentions in the message the user should get eddies for

        Args:
            message (discord.Message): the discord message
            message_type (list): the message_type list to update

        Returns:
            None
        """
        user_id, _ = self._get_ids(message)

        if role_mentions := message.role_mentions:
            message_type.extend("role_mention" for _ in role_mentions)

        if channel_mentions := message.channel_mentions:
            message_type.extend("channel_mention" for _ in channel_mentions)

        if mentions := message.mentions:
            message_type.extend("mention" for mention in mentions if mention.id != user_id)

        if message.mention_everyone:
            message_type.append("everyone_mention")

    def _handle_stickers(
        self, message: discord.Message, guild_id: int, message_type: list[str], message_type_only: bool = False
    ) -> None:
        """Handles stickers.

        Works out if there were any stickers in the message the user should get eddies for

        Args:
            message (discord.Message): the discord message
            guild_id (int): the guild ID
            message_type (list): the message_type list to update
            message_type_only (bool): whether to actually perform actions. Defaults to False.

        Returns:
            None
        """
        if not message.stickers:
            return

        user_id = message.author.id
        channel_id = message.channel.id
        _, is_thread, is_vc = self._get_message_flags(message)
        stickers = message.stickers

        for sticker in stickers:
            sticker_id = sticker.id

            # used a custom sticker!
            message_type.append("custom_sticker")
            sticker_obj = self.server_stickers.get_sticker(guild_id, sticker_id)
            if not sticker_obj:
                continue
            # used a server sticker
            message_type.append("server_sticker")
            if user_id == sticker_obj.created_by:
                continue
            if not message_type_only:
                self.interactions.add_entry(
                    sticker_obj.stid,
                    guild_id,
                    sticker_obj.created_by,
                    channel_id,
                    [
                        "sticker_used",
                    ],
                    message.content,
                    message.created_at,
                    is_thread=is_thread,
                    is_vc=is_vc,
                    additional_keys={"og_mid": message.id},
                )

    def _handle_emojis(
        self, message: discord.Message, guild_id: int, message_type: list[str], message_type_only: bool = False
    ) -> None:
        """Handles emojis.

        Works out if there were any emojis in the message the user should get eddies for

        Args:
            message (discord.Message): the discord message
            guild_id (int): the guild ID
            message_type (list): the message_type list to update
            message_type_only (bool): whether to actually perform actions. Defaults to False.

        Returns:
            None
        """
        emojis = re.findall(r"<:\w*:\d*>", message.content)

        if not emojis:
            return

        user_id, channel_id = self._get_ids(message)
        _, is_thread, is_vc = self._get_message_flags(message)

        for emoji in emojis:
            message_type.append("custom_emoji")
            emoji_id = emoji.strip("<").strip(">").split(":")[-1]

            emoji_obj = self.server_emojis.get_emoji(guild_id, int(emoji_id))
            if not emoji_obj:
                continue

            message_type.append("server_emoji")
            if user_id == emoji_obj.created_by:
                continue
            if not message_type_only:
                self.interactions.add_entry(
                    emoji_obj.eid,
                    guild_id,
                    emoji_obj.created_by,
                    channel_id,
                    ["emoji_used"],
                    message.content,
                    message.created_at,
                    is_thread=is_thread,
                    is_vc=is_vc,
                    additional_keys={"og_mid": message.id},
                )

    async def _handle_references(
        self,
        message: discord.Message,
        guild_id: int,
        message_type: list[str],
        message_type_only: bool = False,
    ) -> bool:
        """Handles references/replies.

        Works out if there were any replies in the message the user should get eddies for

        Args:
            message (discord.Message): the discord message
            guild_id (int): the guild ID
            message_type (list): the message_type list to update
            message_type_only (bool): whether to actually perform actions. Defaults to False.

        Returns:
            None
        """
        if not message.reference:
            return False

        reference = message.reference
        user_id = message.author.id
        is_bot, _, _ = self._get_message_flags(message)

        referenced_message = self.client.get_message(reference.message_id)
        if not referenced_message:
            if reference.channel_id != message.channel.id:
                try:
                    ref_channel = await self.client.fetch_channel(reference.channel_id)
                except (discord.NotFound, discord.Forbidden, discord.HTTPException):
                    # channel was deleted / inaccessible
                    ref_channel = None
            else:
                ref_channel = message.channel

            referenced_message = None
            if ref_channel:
                with contextlib.suppress([discord.NotFound, discord.HTTPException]):
                    referenced_message = await ref_channel.fetch_message(reference.message_id)

        if referenced_message and referenced_message.author.id != user_id:
            message_type.append("reply")
            if not message_type_only:
                self.interactions.add_reply_to_message(
                    reference.message_id,
                    message.id,
                    guild_id,
                    user_id,
                    message.created_at,
                    message.content,
                    is_bot,
                )
            return True
        return False

    async def message_received(
        self,
        message: discord.Message,
        message_type_only: bool = False,
        trigger_actions: bool = True,
    ) -> list | None:
        """Main method for handling when we receive a message.

        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.

        Args:
            message (discord.Message): the message we received
            message_type_only (bool): whether to only process the message type. Defaults to False.
            trigger_actions (bool): whether to trigger message actions. Defaults to True.
        """
        try:
            guild_id = message.guild.id
        except AttributeError:
            # no guild id?
            channel = await self.client.fetch_channel(message.channel.id)
            guild_id = channel.guild.id

        message_content = message.content
        message_type = []

        user_id, channel_id = self._get_ids(message)
        is_bot, is_thread, is_vc = self._get_message_flags(message)

        await self._handle_references(message, guild_id, message_type, message_type_only)
        self._handle_stickers(message, guild_id, message_type, message_type_only)
        self._handle_attachments(message, message_type)
        self._handle_mentions(message, message_type)

        if "https://" in message.content or "http://" in message_content:
            if ".gif" in message.content:
                message_type.append("gif")
            message_type.append("link")

        message_type.append("message")

        if re.match(WORDLE_REGEX, message.content) and any(square for square in ["🟩", "🟨", "⬛", "⬜"]):
            # double check it's a wordle message by presence of emoji
            message_type.append("wordle")

        self._handle_emojis(message, guild_id, message_type, message_type_only)

        if message_type_only:
            return message_type

        self.interactions.add_entry(
            message.id,
            guild_id,
            user_id,
            channel_id,
            message_type,
            message_content,
            message.created_at,
            is_thread=is_thread,
            is_vc=is_vc,
            is_bot=is_bot,
        )

        if trigger_actions:
            # see if we need to act on this messages
            await self.post_message_actions(message, message_type)

        return message_type

    async def post_message_actions(self, message: discord.Message, message_type: list[str]) -> None:
        """Checks message actions preconditions and executes the action if precondition is true.

        Args:
            message (discord.Message): the message to trigger on
            message_type (list): calculated message type
        """
        for cls in self._post_message_action_classes:
            if await cls.pre_condition(message, message_type):
                await cls.run(message)
