
import discord

from discordbot.baseeventclass import BaseEvent
from discordbot.clienteventclasses import OnMessage
from mongo.bsepoints import UserInteractions


class OnThreadCreate(BaseEvent):
    """
        Class for handling on_thread_create event
        """

    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.user_interactions = UserInteractions()
        self.on_message = OnMessage(client, guild_ids, logger)

    async def on_thread_create(self, thread: discord.Thread) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """

        await thread.join()
        self.logger.info(f"Joined {thread.name}")

        if not thread.starting_message:
            starting_message = await thread.fetch_message(thread.id)  # type: discord.Message
        else:
            starting_message = thread.starting_message  # type: discord.Message

        message_type = await self.on_message.message_received(starting_message, True)
        message_type.append("thread_create")

        self.user_interactions.add_entry(
            thread.id,
            thread.guild.id,
            thread.owner_id,
            thread.parent_id,
            message_type,
            starting_message.content,
            thread.created_at
        )
