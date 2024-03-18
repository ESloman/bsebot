"""Task Manager."""

import asyncio
import datetime
from logging import Logger
from zoneinfo import ZoneInfo

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class TaskManager(BaseTask):
    """Class for TaskManager."""

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        tasks: list[BaseTask],
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.tasks = tasks
        self.task = self.task_checker

        self.task_error_logs = {}

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        # init task error dict
        for task in self.tasks:
            _task = {"last_running": now, "error_count": 0, "last_error": None}

            self.task_error_logs[task.qualified_name] = _task

        self.task.start()

    @staticmethod
    def _should_task_be_running(task: BaseTask, now: datetime.datetime) -> bool:
        """Checks whether or not a given task should be running.

        Using the task schedule - validate when the task should be running.
        A task should only be running if our day and hour is within the tasks defined
        schedule. Additionally, the task may define a minute in the schedule - we give the
        task a bit of leeway and have it running for two minutes before and two minutes after it's
        alloted time. This is to allow time for the task to execute properly.

        Tasks should still be checking themselves that they're running at the right time as well.
        This is just to reduce the need to have such ridiculous loops.

        Args:
            task (BaseTask): the task to check
            now (datetime.datetime): the time to check against

        Returns:
            bool: whether the task should be running or not
        """
        try:
            _ = task.schedule
        except NotImplementedError:
            # not implemented the schedule yet
            return True

        if task.schedule.overriden:
            # overriden schedule - pass
            return True

        if (task.schedule.days and now.weekday() not in task.schedule.days) or now.hour not in task.schedule.hours:
            # not the right day or hour for this task - exit
            return False

        if task.schedule.minute and (task.schedule.minute - 2 <= now.minute <= task.schedule.minute + 2):
            # if we define a specific minute - make sure that we're within a few minutes of that time
            # otherwise - exit
            return False

        if task.schedule.dates:
            viable_months = [date.month for date in task.schedule.dates]
            viable_days = [date.day for date in task.schedule.dates]
            if now.month not in viable_months or now.day not in viable_days:
                # not the right day or month - exit
                return False

        return True

    @tasks.loop(minutes=1)
    async def task_checker(self) -> None:
        """Loop that checks that all the tasks are still running.

        Attempts to restart them if they are not running.
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        running_tasks: list[str] = []
        for task in self.tasks:
            task_name = task.qualified_name

            if not self._should_task_be_running(task, now):
                # task shouldn't be running - ensure that it isn't running
                if task.task.is_running() and task.task.next_iteration:
                    # stop the next iteration if there's only
                    if next_iteration := task.task.next_iteration:  # noqa: SIM102
                        # see if we need to stop the next iteration
                        if (next_iteration - now).total_seconds() > 60:  # noqa: PLR2004
                            self.logger.debug("Cancelling %s's next iteration.", task_name)
                            task.task.cancel()

                    self.logger.debug(
                        "Stopping %s - outside of task's schedule (%s, %s).", task_name, now, task.schedule
                    )
                    task.task.stop()
                continue

            # task should be running!
            if not task.task.is_running():
                self.logger.debug("Starting %s - within task's schedule (%s, %s).", task_name, now, task.schedule)
                task.task.start()

            running_tasks.append(task_name)

        self.logger.debug("Running tasks are: %s", running_tasks)

    @task_checker.before_loop
    async def before_task_checker(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
