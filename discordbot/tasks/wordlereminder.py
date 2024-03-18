"""Wordle Reminder Task."""

import asyncio
import datetime
import random
from logging import Logger
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_BOT_ID
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from mongo.datatypes.message import MessageDB


class WordleReminder(BaseTask):
    """Class for Wordle Reminder task."""

    def __init__(
        self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask], start: bool = False
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task on startup. Defaults to False.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.schedule = TaskSchedule(range(7), [19], 30)
        self.task = self.wordle_reminder
        if start:
            self.task.start()

    def _get_reminders_needed(
        self, guild: discord.Guild, start: datetime.datetime, end: datetime.datetime
    ) -> list[MessageDB]:
        """Checks for users that need a reminder to do their wordle.

        Args:
            guild (discord.Guild): the guild to check
            start (datetime.datetime): the start time to check
            end (datetime.datetime): the end time to check

        Returns:
            list[MessageDB]: the list of messages to reminder users
        """
        guild_db = self.guilds.get_guild(guild.id)

        if not guild_db.wordle_reminders:
            # guild isn't configured for wordle reminders
            return []

        wordles_yesterday = self.interactions.query(
            {"guild_id": guild.id, "message_type": "wordle", "timestamp": {"$gte": start, "$lte": end}},
        )

        _start = start + datetime.timedelta(days=1)
        _end = end + datetime.timedelta(days=1)
        wordles_today = self.interactions.query(
            {"guild_id": guild.id, "message_type": "wordle", "timestamp": {"$gte": _start, "$lte": _end}},
        )

        today_ids: list[int] = [m.user_id for m in wordles_today]

        reminders_needed: list[MessageDB] = []
        for message in wordles_yesterday:
            user_id = message.user_id
            if user_id in today_ids:
                continue
            # user hasn't done a wordle
            reminders_needed.append(message)
        return reminders_needed

    @tasks.loop(minutes=1)
    async def wordle_reminder(self) -> None:
        """Loop that reminds users to do their wordle.

        Only reminds users that did their wordle the day before,
        and haven't done it by ~7pm GMT/BST.
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if now.hour != 19 or now.minute != 30:  # noqa: PLR2004
            return

        start = now - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)

        for guild in self.bot.guilds:
            reminders_needed = self._get_reminders_needed(guild, start, end)

            if not reminders_needed:
                self.logger.info("Everyone has done their wordle today!")
                continue

            _messages = self.wordle_reminders.get_all_reminders()
            _messages_list = [_message.name for _message in _messages]

            odds = utilities.calculate_message_odds(
                self.interactions,
                guild.id,
                _messages_list,
                "{mention}",
                [0, 1],
            )

            _messages_sent = [
                "",
            ]
            for reminder in reminders_needed:
                if reminder.user_id == BSE_BOT_ID:
                    # skip bot reminder
                    continue
                channel = await self.bot.fetch_channel(reminder.channel_id)
                await channel.trigger_typing()
                y_message = await channel.fetch_message(reminder.message_id)

                # make sure that we send different messages for each needed reminder
                message = ""
                iterations = 0
                while message in _messages_sent and iterations < 5:  # noqa: PLR2004
                    message = random.choices([message[0] for message in odds], [message[1] for message in odds])[0]
                    iterations += 1

                _messages_sent.append(message)
                message = message.format(mention=f"<@!{reminder.user_id}>")

                self.logger.debug(message)
                await y_message.reply(content=message)

    @wordle_reminder.before_loop
    async def before_wordle_reminder(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
