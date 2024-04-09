"""Bet reminder task."""

import asyncio
import datetime
from zoneinfo import ZoneInfo

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from mongo.datatypes.bet import BetDB


class BetReminder(BaseTask):
    """Class for bet reminder."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start on startup. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule(range(7), range(24))
        self.task = self.bet_reminder
        if start:
            self.task.start()

    async def _check_bet_for_halfway_reminder(self, bet: BetDB, now: datetime.datetime) -> bool:
        """Checks to see if a bet needs a 'halfway' to go reminder.

        Args:
            bet (BetDB): the bet to check
            now (datetime.datetime): the datetime

        Returns:
            bool: whether we sent a message or not
        """
        total_time = (bet.timeout - bet.created).total_seconds()
        half_time = total_time / 2
        half_date = bet.created + datetime.timedelta(seconds=half_time)

        if now > half_date:
            return False

        half_diff = half_date - now

        if half_diff.total_seconds() < 3600:  # noqa: PLR2004
            # within the hour threshold for half way
            channel = await self.bot.fetch_channel(bet.channel_id)
            await channel.trigger_typing()
            message = await channel.fetch_message(bet.message_id)

            num_betters = len(bet.betters.keys())
            eddies_bet = self.user_bets.count_eddies_for_bet(bet)

            msg = (
                "About halfway to go on this bet - don't forget to place some eddies!"
                f"Current there's `{eddies_bet}` eddies on the line from **{num_betters}** betters."
            )

            try:
                _place_command = next(a for a in self.bot.application_commands if a.name == "place")
                msg += f"\n\nUse {_place_command.mention} to place some eddies."
            except (IndexError, AttributeError, TypeError):
                pass

            await message.reply(content=msg, silent=True)
            return True
        return False

    async def _check_bet_for_day_reminder(self, bet: BetDB, now: datetime.datetime) -> bool:
        """Checks to see if a bet needs a day before reminder.

        Args:
            bet (BetDB): the bet to check
            now (datetime.datetime): the current datetime

        Returns:
            bool: whether we sent a message or not
        """
        total_time = (bet.timeout - bet.created).total_seconds()

        if total_time <= 604800 or bet.timeout < now:  # noqa: PLR2004
            # if bet timeout is less than a week - don't bother with reminders
            return False

        diff = bet.timeout - now

        if 82800 <= diff.total_seconds() <= 86400:  # noqa: PLR2004
            # ~ 24 hours to go!
            # send reminder here
            channel = await self.bot.fetch_channel(bet.channel_id)
            await channel.trigger_typing()
            message = await channel.fetch_message(bet.message_id)

            num_betters = len(bet.betters.keys())
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
            return True
        return False

    @tasks.loop(hours=1)
    async def bet_reminder(self) -> None:
        """Loop that takes all our active bets and sends a reminder message."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        for guild in self.bot.guilds:
            active = self.user_bets.get_all_active_bets(guild.id)
            for bet in active:
                if not await self._check_bet_for_day_reminder(bet, now):
                    # only want to send the "halfway" reminder if didn't send the 24 hours to go reminder
                    await self._check_bet_for_halfway_reminder(bet, now)

    @bet_reminder.before_loop
    async def before_bet_reminder(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
