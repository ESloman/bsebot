"""Task for celebrations."""

import asyncio
import datetime
from logging import Logger
from zoneinfo import ZoneInfo

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class Celebrations(BaseTask):
    """Class for celebrations task."""

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

        self.schedule = TaskSchedule(
            days=[],
            hours=[0, 8, 10],
            minute=15,
            dates=[
                datetime.datetime(2021, 12, 25),
                datetime.datetime(2021, 1, 1),
                datetime.datetime(2021, 2, 11),
                datetime.datetime(2021, 5, 14),
            ],
        )

        self.task = self.celebrations
        if start:
            self.task.start()

    async def _christmas_message(self, now: datetime.datetime, channel_id: int) -> bool:
        """Checks our Christmas condition and sends if applicable.

        Args:
            now (datetime.datetime): the current datetime object
            channel_id (int): the channel ID to send to

        Return:
            bool: whether we sent the message or not
        """
        if now.month == 12 and now.day == 25:  # noqa: PLR2004
            # christmas day!!
            if now.hour != 8:  # noqa: PLR2004
                return False
            # now we can send message!
            msg = "Merry Christmas to my favourite server ❤️🎄"
            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return True
        return False

    async def _happy_new_year_message(self, now: datetime.datetime, channel_id: int) -> bool:
        """Checks our New Year condition and sends if applicable.

        Args:
            now (datetime.datetime): the current datetime object
            channel_id (int): the channel ID to send to

        Return:
            bool: whether we sent the message or not
        """
        if now.month == 1 and now.day == 1:
            # new years day!!
            if now.hour != 0:
                return False
            # now we can send message!
            msg = f"Happy New Year! May you be blessed with many eddies in {now.year}! 🎆🎉💋"
            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return True
        return False

    async def _bsebot_birthday_message(self, now: datetime.datetime, channel_id: int) -> bool:
        """Checks our Bot birthday condition and sends if applicable.

        Args:
            now (datetime.datetime): the current datetime object
            channel_id (int): the channel ID to send to

        Return:
            bool: whether we sent the message or not
        """
        if now.month == 2 and now.day == 11:  # noqa: PLR2004
            # my birthday!!
            if now.hour != 10:  # noqa: PLR2004
                return False
            birth_year = self.bot.user.created_at.year
            age = now.year - birth_year
            msg = f"It's my birthday today and I am `{age}` years old! 🍰🧁"
            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return True
        return False

    async def _bse_birthday_message(self, now: datetime.datetime, channel_id: int) -> bool:
        """Checks our BSE birthday condition and sends if applicable.

        Args:
            now (datetime.datetime): the current datetime object
            channel_id (int): the channel ID to send to

        Return:
            bool: whether we sent the message or not
        """
        if now.month == 5 and now.day == 14:  # noqa: PLR2004
            # BSE birthday
            if now.hour != 10:  # noqa: PLR2004
                # already in birthday so can exit func safely
                return False
            bse_created_year = 2016
            age = now.year - bse_created_year
            msg = f"Happy birthday to **Best Summer Ever**! {age} years old today! 🍰🎆🎉"
            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return True
        return False

    @tasks.loop(count=1)
    async def celebrations(self) -> None:
        """Send celebration messages."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if BSE_SERVER_ID not in self.guild_ids:
            # don't currently support any other guilds
            return

        bse_channel_id = self.guilds.get_channel(BSE_SERVER_ID)

        await self._christmas_message(now, bse_channel_id)
        await self._happy_new_year_message(now, bse_channel_id)
        await self._bsebot_birthday_message(now, bse_channel_id)
        await self._bse_birthday_message(now, bse_channel_id)

    @celebrations.before_loop
    async def before_celebrations(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
