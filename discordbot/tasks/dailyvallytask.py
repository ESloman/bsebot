"""Daily valorant task."""

import asyncio
import datetime
import random
from logging import Logger
from zoneinfo import ZoneInfo

from discord.ext import tasks

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.message_strings.valorant_rollcalls import MESSAGES
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class AfterWorkVally(BaseTask):
    """Class for after work vally task."""

    def __init__(
        self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask], start: bool = False
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task by default. Defaults to False.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.schedule = TaskSchedule(days=[0, 1, 2, 3, 4], hours=[15])

        self.task = self.vally_message
        if start:
            self.task.start()

    @tasks.loop(minutes=10)
    async def vally_message(self) -> None:
        """Loop that sends the daily vally rollcall."""
        if BSE_SERVER_ID not in self.guild_ids:
            return

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if now.weekday() not in {0, 1, 2, 3, 4}:
            return

        if now.hour != 15 or not (45 <= now.minute <= 54):  # noqa: PLR2004
            return

        for guild in self.bot.guilds:
            # set this up for theoretically working with other guilds
            # but only work for BSE Server for now
            if guild.id != BSE_SERVER_ID:
                continue

            guild_db = self.guilds.get_guild(guild.id)

            if not guild_db.valorant_rollcall:
                self.logger.info("Valorant rollcall is disabled")
                continue

            valorant_channel = guild_db.valorant_channel
            if not valorant_channel:
                self.logger.info("Valorant channel isn't configured")
                continue

            self.logger.info("Checking for channel interactivity")

            latest_bot_message = next(
                iter(
                    self.interactions.vault.find(
                        {"user_id": self.bot.user.id, "channel_id": valorant_channel, "message_type": "role_mention"},
                        sort=[("timestamp", -1)],
                        limit=1,
                    )
                )
            )

            latest_time = latest_bot_message["timestamp"]

            messages = self.interactions.query(
                {
                    "timestamp": {"$gt": latest_time},
                    "channel_id": valorant_channel,
                    "is_bot": False,
                },
            )

            if not messages:
                self.logger.info(
                    "Not been any messages in the channel since %s - skipping the daily vally message", latest_time
                )
                continue

            self.logger.debug("%s since our last vally rollcall", len(messages))
            self.logger.info("Time to send vally message!")

            _guild = await self.bot.fetch_guild(guild.id)
            channel = await self.bot.fetch_channel(valorant_channel)
            await channel.trigger_typing()

            if role_id := guild_db.valorant_role:
                role = _guild.get_role(role_id)
                _mention = role.mention
            else:
                _mention = "`Valorant`"

            odds = utilities.calculate_message_odds(
                self.interactions,
                _guild.id,
                MESSAGES,
                "{role}",  # noqa: RUF027
                [0, 1],
            )

            message = random.choices([message[0] for message in odds], [message[1] for message in odds])[0]
            message = message.format(role=_mention)

            self.logger.info("Sending daily vally message: %s", message)
            await channel.send(content=message)

    @vally_message.before_loop
    async def before_vally_message(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
