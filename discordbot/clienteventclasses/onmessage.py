import re
from typing import Optional

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import WORDLE_REGEX
from discordbot.message_actions.base import BaseMessageAction  # noqa

# message actions
from discordbot.message_actions.birthday_replies import BirthdayReplies
from discordbot.message_actions.marvel_ad import MarvelComicsAdAction
from discordbot.message_actions.thank_you_replies import ThankYouReplies
from discordbot.message_actions.wordle_reactions import WordleMessageAction


class OnMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client: BSEBot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self._post_message_action_classes = [
            BirthdayReplies(client),
            MarvelComicsAdAction(client),
            ThankYouReplies(client),
            WordleMessageAction(client)
        ]  # type: list[BaseMessageAction]

    async def message_received(
        self,
        message: discord.Message,
        message_type_only: bool = False,
        trigger_actions: bool = True
    ) -> Optional[list]:
        """
        Main method for handling when we receive a message.
        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.
        :param message:
        :param message_type_only:
        :param trigger_actions:
        :return:
        """

        try:
            guild_id = message.guild.id
        except AttributeError:
            # no guild id?
            channel = await self.client.fetch_channel(message.channel.id)
            guild_id = channel.guild.id

        user_id = message.author.id
        channel_id = message.channel.id
        message_content = message.content

        message_type = []

        is_bot = message.author.bot
        is_thread = False
        is_vc = False
        if message.channel.type in [
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread
        ]:
            is_thread = True

        if message.channel.type in [
            discord.ChannelType.voice,
            discord.ChannelType.stage_voice
        ]:
            is_vc = True

        if reference := message.reference:
            referenced_message = self.client.get_message(reference.message_id)
            if not referenced_message:
                if reference.channel_id != message.channel.id:
                    ref_channel = await self.client.fetch_channel(reference.channel_id)
                else:
                    ref_channel = message.channel
                try:
                    referenced_message = await ref_channel.fetch_message(reference.message_id)
                except (discord.NotFound, discord.HTTPException):
                    # reference was deleted
                    referenced_message = None
            if referenced_message and referenced_message.author.id != user_id:
                message_type.append("reply")
                if not message_type_only:
                    self.interactions.add_reply_to_message(
                        reference.message_id, message.id, guild_id, user_id, message.created_at, message_content, is_bot
                    )

        if stickers := message.stickers:
            for sticker in stickers:  # type: discord.StickerItem
                sticker_id = sticker.id
                if sticker_obj := self.server_stickers.get_sticker(guild_id, sticker_id):
                    # used a custom sticker!
                    message_type.append("custom_sticker")

                    if user_id == sticker_obj["created_by"]:
                        continue
                    if not message_type_only:
                        self.interactions.add_entry(
                            sticker_obj["stid"],
                            guild_id,
                            sticker_obj["created_by"],
                            channel_id,
                            ["sticker_used", ],
                            message_content,
                            message.created_at,
                            is_thread=is_thread,
                            is_vc=is_vc,
                            additional_keys={"og_mid": message.id}
                        )

        if message.attachments:
            for attachment in message.attachments:
                message_type.append("attachment")

                # this is only a temporary fix until https://github.com/Pycord-Development/pycord/pull/2016 is merged
                # and pycord officially supports voice messages
                if attachment.filename == "voice-message.ogg":
                    message_type.append("voice_message")

        if role_mentions := message.role_mentions:
            for _ in role_mentions:
                message_type.append("role_mention")

        if channel_mentions := message.channel_mentions:
            for _ in channel_mentions:
                message_type.append("channel_mention")

        if mentions := message.mentions:
            for mention in mentions:
                if mention.id == user_id:
                    continue
                message_type.append("mention")

        if message.mention_everyone:
            message_type.append("everyone_mention")

        if "https://" in message.content or "http://" in message_content:
            if ".gif" in message.content:
                message_type.append("gif")
            message_type.append("link")

        message_type.append("message")

        if re.match(WORDLE_REGEX, message.content):
            message_type.append("wordle")

        if emojis := re.findall(r"<:[a-zA-Z_0-9]*:\d*>", message.content):
            for emoji in emojis:
                emoji_id = emoji.strip("<").strip(">").split(":")[-1]
                if emoji_obj := self.server_emojis.get_emoji(guild_id, int(emoji_id)):
                    # used a custom emoji!
                    message_type.append("custom_emoji")

                    if user_id == emoji_obj["created_by"]:
                        continue
                    if not message_type_only:
                        self.interactions.add_entry(
                            emoji_obj["eid"],
                            guild_id,
                            emoji_obj["created_by"],
                            channel_id,
                            ["emoji_used", ],
                            message_content,
                            message.created_at,
                            is_thread=is_thread,
                            is_vc=is_vc,
                            additional_keys={"og_mid": message.id}
                        )

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
            is_bot=is_bot
        )

        if trigger_actions:
            # see if we need to act on this messages
            await self.post_message_actions(message, message_type)

        return message_type

    async def post_message_actions(self, message: discord.Message, message_type: list):
        for cls in self._post_message_action_classes:
            if await cls.pre_condition(message, message_type):
                await cls.run(message)
