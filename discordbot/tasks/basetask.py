
from logging import Logger

from discord.ext import commands

from discordbot.bsebot import BSEBot
from discordbot.utilities import PlaceHolderLogger

from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.stickers import ServerStickers
from mongo.bsedataclasses import SpoilerThreads
from mongo.bsedataclasses import WordleAttempts
from mongo.bseticketedevents import RevolutionEvent


class BaseTask(commands.Cog):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger = PlaceHolderLogger,
        startup_tasks: list = None
    ) -> None:

        self.bot = bot
        self.guild_ids = guild_ids
        self.logger = logger
        self.finished = False

        if startup_tasks is None:
            startup_tasks = []

        self.startup_tasks = startup_tasks

        # database classes
        self.activities = UserActivities()
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.server_stickers = ServerStickers()
        self.revolutions = RevolutionEvent()
        self.interactions = UserInteractions()
        self.guilds = Guilds()
        self.spoilers = SpoilerThreads()
        self.wordles = WordleAttempts()
        self.spoilers = SpoilerThreads()

    def _check_start_up_tasks(self) -> bool:
        """
        Checks start up tasks
        """
        for task in self.startup_tasks:
            if not task.finished:
                return False
        return True
