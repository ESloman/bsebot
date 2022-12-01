import datetime
from typing import Optional

import discord

import discordbot.clienteventclasses.onmessage
from discordbot.baseeventclass import BaseEvent
from discordbot.constants import BSE_BOT_ID
from mongo.bsepoints import UserInteractions


class OnMessageEdit(BaseEvent):
    """
    Class for handling on_message_edit events from Discord
    """

    def __init__(self, client, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.user_interactions = UserInteractions()
        self.on_message = discordbot.clienteventclasses.onmessage.OnMessage(client, guild_ids, logger)

    async def message_edit(self, before: Optional[discord.Message], after: discord.Message) -> None:
        """Handles our on_message_edit and on_raw_message_edit events

        Args:
            before (Optional[discord.Message]): the message before
            after (discord.Message): the message after
        """
        if after.type in [
            discord.MessageType.application_command
        ]:
            return

        if after.embeds and after.author.id == BSE_BOT_ID:
            return

        if after.channel.type not in [
            discord.ChannelType.text,
            discord.ChannelType.private,
            discord.ChannelType.voice,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.news_thread
        ]:
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

        db_message = self.user_interactions.get_message(guild_id, after.id)

        if not db_message:
            # weird
            message_type = await self.on_message.message_received(after)
            db_message = self.user_interactions.get_message(guild_id, after.id)

        message_type = await self.on_message.message_received(after, True)

        now = datetime.datetime.now()

        self.user_interactions.update(
            {"_id": db_message["_id"]},
            {
                "$set": {
                    "content": after.content,
                    "edited": now,
                    "message_type": message_type
                },
                "$push": {
                    "content_old": db_message["content"]
                },
                "$inc": {
                    "edit_count": 1
                }
            }
        )

        self.logger.info(f"{after.id} was edited - updated DB")
