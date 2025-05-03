"""Our wordle task."""

import asyncio
import datetime
import random
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from discordbot.wordle.data_type import WordleSolve
from discordbot.wordle.wordlesolver import WordleSolver


class WordleTask(BaseTask):
    """Class for our wordle task."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task on startup. Defaults to False.
        """
        super().__init__(bot, startup_tasks)

        self.schedule = TaskSchedule(range(7), [8, 9, 10, 11, 12])

        self.task = self.wordle_message

        self.sent_wordle = False
        self.wait_iters = None

        self._set_wordle()
        if start:
            self.task.start()

    def _set_wordle(self) -> None:
        """Sets `sent_wordle` var based on whether or not we have actually sent wordle today."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        ret = self.wordles.find_wordles_at_timestamp(now, BSE_SERVER_ID)
        self.sent_wordle = ret is not None
        self.schedule.overriden = ret is None

    async def _send_wordles(self, solved_wordle: WordleSolve) -> None:
        """Sends the solved wordle to the necessary guilds.

        Args:
            solved_wordle (WordleSolve): the solved wordle
        """
        # put it into dark mode
        message = solved_wordle.share_text.replace("⬜", "⬛")

        # format 'spoiler message' to output solved word and guesses
        spoiler_message = f"Solved wordle in `{solved_wordle.guess_count}`, word was: || {solved_wordle.actual_word} ||"
        spoiler_message += f". Guesses: || {' -> '.join(solved_wordle.guesses)} ||"

        self.logger.info("Sending wordle message: %s", message)

        for guild in self.bot.guilds:
            guild_db = self.guilds.get_guild(guild.id)
            if not guild_db.wordle:
                self.logger.debug("%s has wordle turned off", guild.name)
                continue

            channel_id = guild_db.wordle_channel
            if not channel_id or not guild_db.wordle:
                self.logger.debug("%s hasn't got a wordle channel configured - skipping", guild.name)
                continue

            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()

            sent_message = await channel.send(content=message, silent=True)

            if solved_wordle.solved:
                await sent_message.reply(content=spoiler_message, silent=True)

            self.wordles.document_wordle(guild.id, solved_wordle)

    @tasks.loop(minutes=10)
    async def wordle_message(self) -> None:
        """Task that does the daily wordle."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if now.hour < 9:  # noqa: PLR2004
            self.wait_iters = None
            self.sent_wordle = False
            self.schedule.overriden = False
            return

        if self.sent_wordle:
            self.schedule.overriden = False
            return

        if self.wait_iters is None:
            self.wait_iters = random.randint(0, 10)

            if now.hour > 15:  # noqa: PLR2004
                self.wait_iters = 0

            self.logger.info("Setting iterations to %s", self.wait_iters)
            return

        if self.wait_iters != 0:
            self.logger.info("Decrementing countdown...")
            self.wait_iters -= 1
            return

        self.logger.info("Setting wordle activity")
        game = discord.Game("Wordle")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

        # actually do wordle now
        wordle_solver = WordleSolver()
        await wordle_solver.setup()

        self.logger.debug("Solving wordle...")
        solved_wordle = await wordle_solver.solve()

        attempts = 1
        while not solved_wordle.solved and attempts < 5:  # noqa: PLR2004
            # if we fail - try again as there's some randomness to it
            self.logger.debug("Failed wordle - attempting again: %s", attempts)
            wordle_solver = WordleSolver()
            await wordle_solver.setup()
            solved_wordle = await wordle_solver.solve()
            attempts += 1

        await self._send_wordles(solved_wordle)

        self.sent_wordle = True
        self.schedule.overriden = False

        self.logger.info("Setting activity back to default")
        listening_activity = discord.Activity(
            name="conversations",
            state="Listening",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )
        await self.bot.change_presence(activity=listening_activity, status=discord.Status.online)

    @wordle_message.before_loop
    async def before_wordle_message(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
