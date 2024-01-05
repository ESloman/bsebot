"""Bet reminder task."""

import asyncio
import datetime
from logging import Logger

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class BetReminder(BaseTask):
    """Class for bet reminder."""

    def __init__(self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask]) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            on_ready (OnReadyEvent): on ready event
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.bet_reminder
        self.task.start()

    @tasks.loop(minutes=60)
    async def bet_reminder(self) -> None:
        """Loop that takes all our active bets and sends a reminder message."""
        now = datetime.datetime.now()
        for guild in self.bot.guilds:
            await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild.id)
            for bet in active:
                timeout = bet["timeout"]
                created = bet["created"]
                total_time = (timeout - created).total_seconds()

                if total_time <= 604800:  # noqa: PLR2004
                    # if bet timeout is less than a week - don't bother with halfway reminders
                    continue

                if now > timeout:
                    continue

                diff = timeout - now

                if 82800 <= diff.total_seconds() <= 86400:  # noqa: PLR2004
                    # ~ 24 hours to go!
                    # send reminder here
                    channel = await self.bot.fetch_channel(bet["channel_id"])
                    await channel.trigger_typing()
                    message = await channel.fetch_message(bet["message_id"])

                    num_betters = len(bet["betters"].keys())
                    eddies_bet = self.user_bets.count_eddies_for_bet(bet)

                    msg = (
                        "Only roughly twenty four hours to get in on this bet!\n"
                        f"Current there's `{eddies_bet}` eddies on the line from **{num_betters}** betters."
                    )

                    try:
                        _place_command = next(a for a in self.bot.application_commands if a.name == "place")
                        msg += f"\n\nUse {_place_command.mention} to place some eddies."
                    except (IndexError, AttributeError, TypeError):
                        pass

                    await message.reply(content=msg)
                    continue

                half_time = total_time / 2
                half_date = created + datetime.timedelta(seconds=half_time)

                if now > half_date:
                    continue

                half_diff = half_date - now

                if half_diff.total_seconds() < 3600:  # noqa: PLR2004
                    # within the hour threshold for half way
                    channel = await self.bot.fetch_channel(bet["channel_id"])
                    await channel.trigger_typing()
                    message = await channel.fetch_message(bet["message_id"])

                    eddies_bet = self.user_bets.count_eddies_for_bet(bet)

                    msg = "About halfway to go on this bet - don't forget to place some eddies!"

                    try:
                        _place_command = next(a for a in self.bot.application_commands if a.name == "place")
                        msg += f"\n\nUse {_place_command.mention} to place some eddies."
                    except (IndexError, AttributeError, TypeError):
                        pass

                    await message.reply(content=msg, silent=True)

    @bet_reminder.before_loop
    async def before_bet_reminder(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
