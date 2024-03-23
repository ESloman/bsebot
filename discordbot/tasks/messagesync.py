"""Task for message sync."""

import asyncio
import datetime
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.onmessage import OnMessage
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class MessageSync(BaseTask):
    """Class for message sync task."""

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        startup_tasks: list[BaseTask],
        on_message: OnMessage,
        start: bool = False,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            on_message (OnMessage): the OnMessage class.
            start (bool): whether to start the task automatically. Defaults to False.
        """
        super().__init__(bot, guild_ids, startup_tasks)
        self.schedule = TaskSchedule(range(7), [2], minute=15, overriden=True)
        self.task = self.message_sync
        self.on_message = on_message
        if start:
            self.task.start()

    @staticmethod
    async def get_unsynced_messages(
        channel: discord.TextChannel | discord.Thread,
        message_ids: list[int],
        before: datetime.datetime | None = None,
        after: datetime.datetime | None = None,
    ) -> list[discord.Message]:
        """Retrieves messages from a discord Channel and checks if they're in our cache already.

        Returns messages that aren't in the cache.

        Args:
            channel (discord.TextChannel | discord.Thread): the channel/thread to check for
            message_ids (list[int]): list of cached message IDs
            before (datetime.datetime, optional): latest time to check. Defaults to None.
            after (datetime.datetime, optional): earliest time to check. Defaults to None.

        Returns:
            list[discord.Message]: list of unsynced messages
        """
        _messages_to_sync = []
        async for message in channel.history(limit=None, oldest_first=False, after=after, before=before):
            if message.id in message_ids:
                # already got this message ID synced
                continue
            _messages_to_sync.append(message)

        return _messages_to_sync

    async def _message_sync(self, channel: discord.TextChannel | discord.Thread) -> None:
        """Checks a given channel for unsynced messages.

        Initially goes back a week to find unsynced messages, but will go back further
        if it finds unsynced messages for the given channel.

        Args:
            channel (discord.TextChannel | discord.Thread): the channel to check
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        offset_days = 7
        offset = now - datetime.timedelta(days=offset_days)
        before = now

        self.logger.info("Checking %s for unsynced messages", channel.name)

        _cached_messages = self.interactions.get_all_messages_for_channel(channel.guild.id, channel.id)
        _cached_ids = [c.message_id for c in _cached_messages]

        sync = True
        while sync:
            unsynced = await self.get_unsynced_messages(channel, _cached_ids, before, offset)

            if not unsynced:
                sync = False
                continue

            self.logger.info("Found %s unsynced messages in %s", len(unsynced), channel.name)

            for message in unsynced:
                _trigger_actions = False
                if (datetime.datetime.now(tz=datetime.UTC) - message.created_at).total_seconds() < 120:  # noqa: PLR2004
                    # if message is relatively new; trigger actions
                    # for when we miss a message during a restart
                    self.logger.info("%s was created less than two minutes ago - WILL trigger actions", message.id)
                    _trigger_actions = True
                await self.on_message.message_received(message, False, _trigger_actions)

            before = offset
            offset_days += 30
            offset = now - datetime.timedelta(days=offset_days)
            self.logger.debug("Setting offset to %s and looping again", offset)

    @tasks.loop(count=1)
    async def message_sync(self) -> None:
        """Loop that makes sure all messages are synced correctly."""
        for guild in self.bot.guilds:
            self.logger.debug("Checking %s for unsynced messages", guild.name)

            for channel in guild.channels:
                if type(channel) not in {discord.TextChannel, discord.Thread}:
                    continue

                try:
                    await self._message_sync(channel)
                except discord.Forbidden:
                    self.logger.debug("Don't have permissions to access %s", channel.name)
                    continue
                # check threads for channel
                archived = await channel.archived_threads().flatten()
                for thread in channel.threads + archived:
                    try:
                        await self._message_sync(thread)
                    except discord.Forbidden:
                        self.logger.debug("Don't have permissions to access %s", channel.name)
                        continue
            self.logger.debug("Finished sync for %s", guild.name)
        self.schedule.overriden = False

    @message_sync.before_loop
    async def before_message_sync(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
