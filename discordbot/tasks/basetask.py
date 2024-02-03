"""Our BaseTask class.

This is our implementation of BaseTask. It should provide a common descendant for all tasks.
This is where we should initialise all the database Collection classes we want to use
in the various tasks.
"""

from logging import Logger

from discord.ext import commands, tasks

from discordbot.bsebot import BSEBot
from discordbot.utilities import PlaceHolderLogger
from mongo.bsedataclasses import BotActivities, SpoilerThreads, WordleAttempts, WordleReminders
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.channels import GuildChannels
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.reminders import ServerReminders
from mongo.bsepoints.stickers import ServerStickers
from mongo.bseticketedevents import RevolutionEvent


class BaseTask(commands.Cog):
    """Our BaseTask class."""

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger = PlaceHolderLogger,
        startup_tasks: list | None = None,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        self.bot: BSEBot = bot
        self.guild_ids: list[int] = guild_ids
        self.logger: Logger = logger
        self.finished: bool = False

        if startup_tasks is None:
            startup_tasks = []

        self.startup_tasks: list[BaseTask] = startup_tasks

        self._task = None

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
        self._task = task

    def cog_unload(self) -> None:
        """Method for cancelling the loop."""
        self.task.cancel()
