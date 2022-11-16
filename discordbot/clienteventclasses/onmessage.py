import re
from typing import Optional

import discord

from discordbot.baseeventclass import BaseEvent
from mongo.bsepoints import UserInteractions


class OnMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.user_interactions = UserInteractions()

    async def message_received(self, message: discord.Message, message_type_only=False) -> Optional[list]:
        """
        Main method for handling when we receive a message.
        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.
        :param message:
        :param message_type_only:
        :return:
        """

        guild_id = message.guild.id
        user_id = message.author.id
        channel_id = message.channel.id
        message_content = message.content

        if guild_id not in self.guild_ids:
            return

        message_type = []

        is_thread = False
        if message.channel.type in [
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread
        ]:
            is_thread = True

        if reference := message.reference:
            referenced_message = self.client.get_message(reference.message_id)
            if not referenced_message:
                if reference.channel_id != message.channel.id:
                    ref_channel = await self.client.fetch_channel(reference.channel_id)
                else:
                    ref_channel = message.channel
                try:
                    referenced_message = await ref_channel.fetch_message(reference.message_id)
                except discord.NotFound:
                    # reference was deleted
                    referenced_message = None
            if referenced_message and referenced_message.author.id != user_id:
                message_type.append("reply")
                if not message_type_only:
                    self.user_interactions.add_reply_to_message(
                        reference.message_id, message.id, guild_id, user_id, message.created_at, message_content
                    )

        if stickers := message.stickers:
            for sticker in stickers:  # type: discord.StickerItem
                sticker_id = sticker.id
                if sticker_obj := self.server_stickers.get_sticker(guild_id, sticker_id):
                    # used a custom emoji!
                    message_type.append("custom_sticker")

                    if user_id == sticker_obj["created_by"]:
                        continue
                    if not message_type_only:
                        self.user_interactions.add_entry(
                            sticker_obj["stid"],
                            guild_id,
                            sticker_obj["created_by"],
                            channel_id,
                            ["sticker_used", ],
                            message_content,
                            message.created_at,
                            is_thread=is_thread,
                            additional_keys={"og_mid": message.id}
                        )

        if message.attachments:
            message_type.append("attachment")

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

        if re.match(r"Wordle \d?\d\d\d \d/\d\n\n", message.content):
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
                        self.user_interactions.add_entry(
                            emoji_obj["eid"],
                            guild_id,
                            emoji_obj["created_by"],
                            channel_id,
                            ["emoji_used", ],
                            message_content,
                            message.created_at,
                            is_thread=is_thread,
                            additional_keys={"og_mid": message.id}
                        )

        if message_type_only:
            return message_type

        self.user_interactions.add_entry(
            message.id,
            guild_id,
            user_id,
            channel_id,
            message_type,
            message_content,
            message.created_at,
            is_thread=is_thread
        )
