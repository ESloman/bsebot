
import asyncio
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.onmessage import OnMessage
from discordbot.tasks.basetask import BaseTask


class MessageSync(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        on_message: OnMessage
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.on_message = on_message
        self.message_sync.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.message_sync.cancel()

    async def get_unsynced_messages(
        self,
        channel: discord.TextChannel | discord.Thread,
        message_ids: list[int],
        before: datetime.datetime = None,
        after: datetime.datetime = None
    ) -> list[discord.Message]:
        """
        Retrieves messages from a discord Channel and checks if they're in our cache already
        Returns messages that aren't in the cache

        Args:
            channel (discord.TextChannel | discord.Thread): the channel/thread to check for
            message_ids (list[int]): list of cached message IDs
            before (datetime.datetime, optional): latest time to check. Defaults to None.
            after (datetime.datetime, optional): earliest time to check. Defaults to None.

        Returns:
            list[discord.Message]: list of unsynced messages
        """

        _messages_to_sync = []
        async for message in channel.history(
            limit=None,
            oldest_first=False,
            after=after,
            before=before
        ):
            if message.id in message_ids:
                # already got this message ID synced
                continue
            _messages_to_sync.append(message)

        return _messages_to_sync

    async def _message_sync(
        self,
        channel: discord.TextChannel | discord.Thread
    ):
        """
        Checks a given channel for unsynced messages
        Initially goes back a week to find unsynced messages, but will go back further
        if it finds unsynced messages for the given channel.

        Args:
            channel (discord.TextChannel | discord.Thread): the channel to check
        """

        now = datetime.datetime.now()
        offset_days = 7
        offset = now - datetime.timedelta(days=offset_days)
        before = now

        self.logger.info(f"Checking {channel.name} for unsynced messages")

        _cached_messages = self.interactions.get_all_messages_for_channel(
                channel.guild.id,
                channel.id
            )
        _cached_ids = [c["message_id"] for c in _cached_messages]

        sync = True
        while sync:

            unsynced = await self.get_unsynced_messages(channel, _cached_ids, before, offset)

            if not unsynced:
                sync = False
                continue

            self.logger.info(f"Found {len(unsynced)} unsynced messages in {channel.name}")

            for message in unsynced:
                await self.on_message.message_received(message, False)

            before = offset
            offset_days += 30
            offset = now - datetime.timedelta(days=offset_days)
            self.logger.info(f"Setting offset to {offset} and looping again")

    @tasks.loop(hours=16)
    async def message_sync(self):
        """
        Loop that makes sure all messages are synced correctly
        :return:
        """

        for guild in self.bot.guilds:

            self.logger.info(f"Checking {guild.name} for unsynced messages")

            for channel in guild.channels:

                if type(channel) not in [discord.TextChannel, discord.Thread]:
                    continue

                await self._message_sync(channel)

                # check threads for channel
                archived = await channel.archived_threads().flatten()
                for thread in channel.threads + archived:
                    await self._message_sync(thread)

            self.logger.info(f"Finished sync for {guild.name}")

    @message_sync.before_loop
    async def before_message_sync(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
