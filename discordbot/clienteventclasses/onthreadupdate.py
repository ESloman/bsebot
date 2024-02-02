"""Contains our OnThreadUpdate class.

Handles on_thread_update events.
"""

import logging

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from mongo.bsedataclasses import SpoilerThreads


class OnThreadUpdate(BaseEvent):
    """Class for handling on_thread_update event."""

    def __init__(self, client: BSEBot, guild_ids: list[int], logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        super().__init__(client, guild_ids, logger)
        self.spoiler_threads = SpoilerThreads()

    async def on_update(self, _: discord.Thread, after: discord.Thread) -> None:
        """Handles on_thread_update events.

        Args:
            _ (discord.Thread): the thread before
            after (discord.Thread): the thread after
        """
        self.logger.info("Thread %s has been updated - checking to see if it needs joining", after.name)
        thread_members = await after.fetch_members()
        member_ids = [member.id for member in thread_members]
        if self.client.user.id not in member_ids:
            await after.join()
            self.logger.info("Joined %s", after.name)

        if not self.spoiler_threads.get_thread_by_id(after.guild.id, after.id):
            self.spoiler_threads.insert_spoiler_thread(
                after.guild.id,
                after.id,
                after.name,
                after.created_at,
                after.owner_id,
            )
