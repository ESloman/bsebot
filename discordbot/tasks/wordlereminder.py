"""Wordle Reminder Task."""

import asyncio
import datetime
import random
from logging import Logger
from typing import TYPE_CHECKING

from discord.ext import tasks

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_BOT_ID
from discordbot.tasks.basetask import BaseTask

if TYPE_CHECKING:
    from mongo.datatypes.message import MessageDB


class WordleReminder(BaseTask):
    """Class for Wordle Reminder task."""

    def __init__(self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask]) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.wordle_reminder
        self.task.start()

    @tasks.loop(minutes=60)
    async def wordle_reminder(self) -> None:  # noqa: C901
        """Loop that reminds users to do their wordle.

        Only reminds users that did their wordle the day before,
        and haven't done it by ~7pm GMT/BST.
        """
        now = datetime.datetime.now()

        if now.hour != 19:  # noqa: PLR2004
            return

        start = now - datetime.timedelta(days=1)
        start = start.replace(hour=0, minute=0, second=0, microsecond=1)
        end = start.replace(hour=23, minute=59, second=59)

        if not utilities.is_utc(now):
            # need to add UTC offset
            start = utilities.add_utc_offset(start)
            end = utilities.add_utc_offset(end)

        for guild in self.bot.guilds:
            guild_db = self.guilds.get_guild(guild.id)

            if not guild_db.wordle_reminders:
                # guild isn't configured for wordle reminders
                return

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
                channel = await self.bot.fetch_channel(reminder["channel_id"])
                await channel.trigger_typing()
                channel_id = reminder["channel_id"]

                if channel_id != channel.id:
                    self.logger.info(
                        "%s for wordle message (%) didn't match %s", channel_id, reminder["message_id"], channel.id
                    )
                    continue

                y_message = await channel.fetch_message(reminder["message_id"])

                # make sure that we send different messages for each needed reminder
                message = ""
                while message in _messages_sent:
                    message = random.choices([message[0] for message in odds], [message[1] for message in odds])[0]

                _messages_sent.append(message)
                message = message.format(mention=y_message.author.mention)

                self.logger.info(message)
                await y_message.reply(content=message)

    @wordle_reminder.before_loop
    async def before_wordle_reminder(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
