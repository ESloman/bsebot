"""Our BaseTask class.

This is our implementation of BaseTask. It should provide a common descendant for all tasks.
This is where we should initialise all the database Collection classes we want to use
in the various tasks.
"""

import dataclasses
import datetime

from discord.ext import commands, tasks
from slomanlogger import SlomanLogger

from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from mongo.bsedataclasses import BotActivities, SpoilerThreads, WordleAttempts, WordleReminders
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.channels import GuildChannels
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.stickers import ServerStickers
from mongo.bseticketedevents import RevolutionEvent


@dataclasses.dataclass
class TaskSchedule:
    """Defines a task's schedule."""

    days: list[int]
    """The days of the week a task should be running."""
    hours: list[int]
    """The hours a given task should be running."""
    minute: int | None = None
    """The minute a task should run at. Defaults to None."""
    overriden: bool = False
    """Whether we're overriding the schedule and forcing it to run."""
    dates: list[datetime.datetime] | None = None
    """Particular dates the task should be running."""


class BaseTask(commands.Cog):
    """Our BaseTask class."""

    def __init__(
        self,
        bot: BSEBot,
        startup_tasks: list | None = None,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        self.bot: BSEBot = bot
        self.logger = SlomanLogger("bsebot")
        self.finished: bool = False

        if startup_tasks is None:
            startup_tasks = []

        self.startup_tasks: list[BaseTask] = startup_tasks

        self._task: tasks.Loop | None = None
        self._schedule: TaskSchedule | None = None

        self.embed_manager = EmbedManager()

        # database classes
        self.activities = UserActivities()
        self.bot_activities = BotActivities()
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.server_stickers = ServerStickers()
        self.revolutions = RevolutionEvent()
        self.interactions = UserInteractions()
        self.guilds = Guilds()
        self.server_reminders = ServerReminders()
        self.spoilers = SpoilerThreads()
        self.wordles = WordleAttempts()
        self.wordle_reminders = WordleReminders()
        self.guild_channels = GuildChannels()

    def _check_start_up_tasks(self) -> bool:
        """Checks start up tasks."""
        return all(task.finished for task in self.startup_tasks)

    @property
    def task(self) -> tasks.Loop:
        """Property for this task."""
        return self._task

    @task.setter
    def task(self, task: tasks.Loop) -> None:
        """Task setter."""
        self._task = task

    @property
    def schedule(self) -> TaskSchedule:
        """Schedule property."""
        return self._schedule

    @schedule.setter
    def schedule(self, _schedule: TaskSchedule) -> None:
        """Schedule setter."""
        self._schedule = _schedule

    def cog_unload(self) -> None:
        """Method for cancelling the loop."""
        self.task.cancel()
