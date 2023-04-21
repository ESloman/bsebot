
import asyncio
import datetime
from logging import Logger

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class TaskManager(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        tasks: list[BaseTask]
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.tasks = tasks
        self.task = self.task_checker

        self.task_error_logs = {}

        now = datetime.datetime.now()

        # init task error dict
        for task in self.tasks:
            _task = {
                "last_running": now,
                "error_count": 0,
                "last_error": None
            }

            self.task_error_logs[task.qualified_name] = _task

        self.task.start()

    @tasks.loop(minutes=15)
    async def task_checker(self):
        """
        Loop that checks that all the tasks are still running.
        Attempts to restart them if they are not running.
        """

        now = datetime.datetime.now()

        for task in self.tasks:

            task_name = task.qualified_name

            if not task.task.is_running():

                self.task_error_logs[task_name]["error_count"] += 1
                self.task_error_logs[task_name]["last_error"] = now

                self.logger.info(f"{task_name} isn't running? Attempting to restart.")
                task.task.start()

            else:
                self.task_error_logs[task_name]["last_running"] = now

    @task_checker.before_loop
    async def before_task_checker(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
