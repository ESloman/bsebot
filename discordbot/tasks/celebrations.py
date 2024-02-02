"""Task for celebrations."""

import asyncio
import datetime
from logging import Logger

import pytz
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.tasks.basetask import BaseTask


class Celebrations(BaseTask):
    """Class for celebrations task."""

    def __init__(self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask]) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.celebrations
        self.task.start()

    @tasks.loop(minutes=15)
    async def celebrations(self) -> None:  # noqa: PLR0911
        """Send celebration message."""
        now = datetime.datetime.now(tz=pytz.utc)

        if BSE_SERVER_ID not in self.guild_ids:
            return

        if now.month == 12 and now.day == 25:  # noqa: PLR2004
            # christmas day!!
            if now.hour != 8 or not (15 <= now.minute < 30):  # noqa: PLR2004
                # already in christmas day - can exit func safely
                return
            # now we can send message!
            msg = "Merry Christmas to my favourite server ❤️🎄"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 1 and now.day == 1:
            # new years day!!
            if now.hour != 0 or not (0 <= now.minute < 15):  # noqa: PLR2004
                # already in NY so we can exit func safely
                return
            # now we can send message!
            msg = f"Happy New Year! May you be blessed with many eddies in {now.year}! 🎆🎉💋"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 2 and now.day == 11:  # noqa: PLR2004
            # my birthday!!
            if now.hour != 10 or not (0 <= now.minute < 15):  # noqa: PLR2004
                # already in birthday so can exit func safely
                return
            birth_year = self.bot.user.created_at.year
            age = now.year - birth_year
            msg = f"It's my birthday today and I am `{age}` years old! 🍰🧁"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 5 and now.day == 14:  # noqa: PLR2004
            # BSE birthday
            if now.hour != 10 or not (0 <= now.minute < 15):  # noqa: PLR2004
                # already in birthday so can exit func safely
                return
            bse_created_year = 2016
            age = now.year - bse_created_year
            msg = f"Happy birthday to **Best Summer Ever**! {age} years old today! 🍰🎆🎉"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)

    @celebrations.before_loop
    async def before_celebrations(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
