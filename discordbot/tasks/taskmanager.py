"""Task Manager."""

import datetime
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
        startup_tasks: list[BaseTask],
        tasks: list[BaseTask],
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            startup_tasks (list | None, optional): the list of startup tasks.
            tasks (list[BaseTask]): the list of all the other tasks to manager.
        """
        super().__init__(bot, guild_ids, startup_tasks)
        self.task = self.task_checker
        self.tasks = tasks
        self.task.start()

    def _should_task_be_running(self, task: BaseTask, now: datetime.datetime) -> bool:
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
        if not task.schedule or task.schedule.overriden:
            # overriden schedule - pass
            return True

        should_run: bool = True
        if task.schedule.days and now.weekday() not in task.schedule.days:
            # not the right day or hour for this task - exit
            self.logger.debug(
                "%s: weekday %s not in scheduled days %s", task.qualified_name, now.weekday(), task.schedule.days
            )
            should_run = False

        if should_run and now.hour not in task.schedule.hours:
            self.logger.debug(
                "%s: hour %s not in scheduled hours %s", task.qualified_name, now.hour, task.schedule.hours
            )
            should_run = False

        if should_run and task.schedule.minute and now.minute != task.schedule.minute:
            # if we define a specific minute - make sure that we're within a few minutes of that time
            # otherwise - exit
            self.logger.debug("%s: minute %s not as scheduled %s", task.qualified_name, now.hour, task.schedule.minute)
            should_run = False

        if should_run and task.schedule.dates:
            viable_months = [date.month for date in task.schedule.dates]
            viable_days = [date.day for date in task.schedule.dates]
            if now.month not in viable_months or now.day not in viable_days:
                # not the right day or month - exit
                should_run = False

        return should_run

    def _stop_task(self, task: BaseTask, now: datetime.datetime) -> None:
        """Stops a given task.

        Also attempts to cancel if there's a next iteration scheduled.

        Args:
            task (BaseTask): the task to stop
            now (datetime.datetime): the datetime object
        """
        if task.task.is_running() and task.task.next_iteration:
            # stop the next iteration if there's only
            # see if we need to stop the next iteration
            if (task.task.next_iteration - now).total_seconds() > 60:  # noqa: PLR2004
                self.logger.debug("Cancelling %s's next iteration.", task.qualified_name)
                task.task.cancel()

            self.logger.debug(
                "Stopping %s - outside of task's schedule (%s, %s).", task.qualified_name, now, task.schedule
            )
            task.task.stop()

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
                self._stop_task(task, now)
                continue

            if not self._check_start_up_tasks() and task_name not in [
                stask.qualified_name for stask in self.startup_tasks
            ]:
                # startup tasks haven't finished yet and this isn't one - skip
                continue

            # task should be running!
            if not task.task.is_running():
                self.logger.debug("Starting %s - within task's schedule (%s, %s).", task_name, now, task.schedule)
                task.task.start()

            running_tasks.append(task_name)
            if task.task.next_iteration:
                self.logger.debug("%s is running - next iteration is: %s", task_name, task.task.next_iteration)

        self.logger.debug("Running tasks are: %s", running_tasks)

    @task_checker.before_loop
    async def before_task_checker(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
