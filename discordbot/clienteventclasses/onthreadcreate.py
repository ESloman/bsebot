"""Contains our OnThreadCreate class.

Handles on_thread_create events.
"""

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.clienteventclasses.onmessage import OnMessage
from mongo.bsedataclasses import SpoilerThreads


class OnThreadCreate(BaseEvent):
    """Class for handling on_thread_create event."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self.on_message = OnMessage(client)
        self.threads = SpoilerThreads()

    async def on_thread_create(self, thread: discord.Thread) -> None:
        """Method called for on_ready event.

        Makes sure we have an entry for every user in each guild.

        Args:
            thread (discord.Thread): the thread
        """
        await thread.join()
        self.logger.info("Joined %s", thread.name)

        if not thread.starting_message:
            starting_message = await thread.fetch_message(thread.id)  # type: discord.Message
        else:
            starting_message = thread.starting_message  # type: discord.Message

        message_type = await self.on_message.message_received(starting_message, True)
        message_type.append("thread_create")

        self.interactions.add_entry(
            starting_message.id,
            thread.guild.id,
            thread.owner_id,
            thread.id,
            message_type,
            starting_message.content,
            thread.created_at,
            is_thread=True,
        )

        if not self.threads.get_thread_by_id(thread.guild.id, thread.id):
            self.threads.insert_spoiler_thread(
                thread.guild.id,
                thread.id,
                thread.name,
                thread.created_at,
                thread.owner_id,
            )

        if "spoiler" in thread.name.lower():
            msg = (
                "A wild thread appears! If you want this thread to receive the weekly mute reminder then you can use "
                "the `/config` command to configure the thread data."
            )
            await thread.send(content=msg, silent=True)
