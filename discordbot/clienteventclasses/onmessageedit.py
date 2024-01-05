"""Contains our OnMessageEdit class.

Handles on_message_edit and on_raw_message_edit events.
"""

import datetime
import logging

import discord

import discordbot.clienteventclasses.onmessage
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import BSE_BOT_ID


class OnMessageEdit(BaseEvent):
    """Class for handling on_message_edit events from Discord."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.on_message = discordbot.clienteventclasses.onmessage.OnMessage(client, guild_ids, logger)

    async def message_edit(self, before: discord.Message | None, after: discord.Message) -> None:
        """Handles our on_message_edit and on_raw_message_edit events.

        Args:
            before (Optional[discord.Message]): the message before
            after (discord.Message): the message after
        """
        if after.flags.ephemeral:
            return

        if after.type == discord.MessageType.application_command:
            return

        if after.embeds and after.author.id == BSE_BOT_ID:
            return

        if after.channel.type not in {
            discord.ChannelType.text,
            discord.ChannelType.private,
            discord.ChannelType.voice,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread,
        }:
            return

        if before and before.content == after.content and after.embeds and not before.embeds:
            # edit is just adding an embed - skip
            return

        try:
            guild_id = after.guild.id
        except AttributeError:
            # no guild id?
            channel = await self.client.fetch_channel(after.channel.id)
            guild_id = channel.guild.id

        db_message = self.interactions.get_message(guild_id, after.id)

        if not db_message:
            # weird
            message_type = await self.on_message.message_received(after)
            db_message = self.interactions.get_message(guild_id, after.id)
            if not db_message:
                self.logger.debug("Message couldn't be processed: %s %s", message_type, after)
                return

        message_type = await self.on_message.message_received(after, True)

        now = datetime.datetime.now()

        self.interactions.update(
            {"_id": db_message["_id"]},
            {
                "$set": {"content": after.content, "edited": now, "message_type": message_type},
                "$push": {"content_old": db_message["content"]},
                "$inc": {"edit_count": 1},
            },
        )

        self.logger.debug("%s was edited - updated DB", after.id)
