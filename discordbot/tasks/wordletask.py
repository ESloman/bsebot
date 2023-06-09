
import asyncio
import datetime
from logging import Logger
import random

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.tasks.basetask import BaseTask
from discordbot.wordle.wordlesolver import WordleSolver


class WordleTask(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.wordle_message

        self.sent_wordle = False
        self.wait_iters = None

        self._set_wordle()
        self.task.start()

    def _set_wordle(self):
        """
        Sets `sent_wordle` var based on whether or not we have actually sent wordle today
        """
        now = datetime.datetime.now()

        ret = self.wordles.query(
            {
                "guild_id": BSE_SERVER_ID,
                "timestamp": f"{now.strftime('%Y-%m-%d')}"
            }
        )
        self.sent_wordle = bool(ret)

    @tasks.loop(minutes=10)
    async def wordle_message(self):
        """
        Task that does the daily wordle
        """

        now = datetime.datetime.now()

        if now.hour < 9:
            self.wait_iters = None
            self.sent_wordle = False
            return

        if self.sent_wordle:
            return

        if self.wait_iters is None:
            self.wait_iters = random.randint(0, 10)

            if now.hour > 15:
                self.wait_iters = 0

            self.logger.info(f"Setting iterations to {self.wait_iters}")
            return

        if self.wait_iters != 0:
            self.logger.info("Decrementing countdown...")
            self.wait_iters -= 1
            return

        # wait iters is 0
        assert self.wait_iters == 0

        self.logger.info("Setting wordle activity")
        game = discord.Game("Wordle")
        await self.bot.change_presence(status=discord.Status.online, activity=game)

        # actually do wordle now

        wordle_solver = WordleSolver(self.logger)
        await wordle_solver.setup()

        self.logger.debug("Solving wordle...")
        solved_wordle = await wordle_solver.solve()

        attempts = 1
        while not solved_wordle.solved and attempts < 5:
            # if we fail - try again as there's some randomness to it
            self.logger.debug(f"Failed wordle - attempting again: {attempts}")
            wordle_solver = WordleSolver(self.logger)
            await wordle_solver.setup()
            solved_wordle = await wordle_solver.solve()
            attempts += 1

        # put it into dark mode
        message = solved_wordle.share_text.replace("⬜", "⬛")
        spoiler_message = (
            f"Solved wordle in `{solved_wordle.guess_count}`, "
            f"word was: || {solved_wordle.actual_word} ||"
        )

        self.logger.info(f"Sending wordle message: {message}")
        for guild in self.bot.guilds:

            guild_db = self.guilds.get_guild(guild.id)
            if not guild_db.get("wordle"):
                self.logger.info(f"{guild.name} has wordle turned off")
                continue

            channel_id = guild_db.get("wordle_channel")
            if not channel_id or not guild_db.get("wordle"):
                self.logger.info(f"{guild.name} hasn't got a wordle channel configured - skipping")
                continue

            channel = await self.bot.fetch_channel(channel_id)
            await channel.trigger_typing()

            sent_message = await channel.send(content=message, silent=True)

            if solved_wordle.solved:
                await sent_message.reply(content=spoiler_message, silent=True)

            self.wordles.document_wordle(guild.id, solved_wordle)

        self.sent_wordle = True

        self.logger.info("Setting activity back to default")
        listening_activity = discord.Activity(
            name="conversations",
            state="Listening",
            type=discord.ActivityType.listening,
            details="Waiting for commands!"
        )
        await self.bot.change_presence(activity=listening_activity, status=discord.Status.online)

    @wordle_message.before_loop
    async def before_wordle_message(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
