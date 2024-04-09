"""Contains our OnMessageEdit class.

Handles on_message_edit and on_raw_message_edit events.
"""

import datetime
from zoneinfo import ZoneInfo

import discord

import discordbot.clienteventclasses.onmessage
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import BSE_BOT_ID


class OnMessageEdit(BaseEvent):
    """Class for handling on_message_edit events from Discord."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self.on_message = discordbot.clienteventclasses.onmessage.OnMessage(client)

    @staticmethod
    def _check_condition(before: discord.Message | None, after: discord.Message) -> bool:
        """Checks to see if we care about the message being edited.

        Args:
            before (discord.Message | None): message before
            after (discord.Message): message after

        Returns:
            bool: whether to continue with this message or not
        """
        if after.flags.ephemeral or after.type == discord.MessageType.application_command:
            # message is ephemeral or an application command
            return False

        if after.embeds and after.author.id == BSE_BOT_ID:
            # message is a bot message with embeds
            return False

        if after.channel.type not in {
            discord.ChannelType.text,
            discord.ChannelType.private,
            discord.ChannelType.voice,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread,
        } or isinstance(after.channel, discord.DMChannel):
            return False

        # edit is just adding an embed - skip
        return not (before and before.content == after.content and after.embeds and not before.embeds)

    async def message_edit(self, before: discord.Message | None, after: discord.Message) -> None:
        """Handles our on_message_edit and on_raw_message_edit events.

        Args:
            before (Optional[discord.Message]): the message before
            after (discord.Message): the message after
        """
        if not self._check_condition(before, after):
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
                self.logger.warning("Message couldn't be processed: %s %s", message_type, after)
                return

        message_type = await self.on_message.message_received(after, True)

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        self.interactions.update(
            {"_id": db_message._id},  # noqa: SLF001
            {
                "$set": {"content": after.content, "edited": now, "message_type": message_type},
                "$push": {"content_old": db_message.content},
                "$inc": {"edit_count": 1},
            },
        )

        self.logger.debug("%s was edited - updated DB", after.id)
