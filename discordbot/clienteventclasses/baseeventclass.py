"""Base event class.

All client event classes inherit from this. Adds a bunch of useful properties for
it's children to use.
"""

from typing import Any

import discord
from slomanlogger import SlomanLogger

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.stickers import ServerStickers
from mongo.bseticketedevents import RevolutionEvent


class BaseEvent:
    """This is a BaseEvent class that all events will inherit from.

    Basically just sets up all the vars that events will need and rely on.
    """

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method that creates database Collections and various variables.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list[int]): list of supported guild_ids
            logger (logging.Logger): the logger to use
        """
        self.activities = UserActivities()
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.server_stickers = ServerStickers()
        self.revolutions = RevolutionEvent()
        self.interactions = UserInteractions()
        self.guilds = Guilds()
        self.client = client
        self.guild_ids = guild_ids
        self.embed_manager = EmbedManager()
        self.logger = SlomanLogger("bsebot")

    def _add_event_type_to_activity_history(
        self,
        user: discord.Member,
        guild_id: int,
        _type: ActivityTypes,
        **params: dict[str, Any],
    ) -> None:
        """Adds an event type to activity history.

        Args:
            user (discord.Member): the user that triggered the activity
            guild_id (int): the guild ID the activity happened for
            _type (ActivityTypes): the activity type,
            params (dict[str, Any]): additional parameters to provided to the activity
        """
        self.logger.info(
            "%s triggered by %s with %s",
            _type.name,
            user.name,
            params,
        )

        self.activities.add_activity(user.id, guild_id, _type, **params)
