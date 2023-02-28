
"""
Base event class.
All client event classes inherit from this. Adds a bunch of useful classes for
it's children to use.
"""

import datetime
import logging

import discord

from discordbot.bsebot import BSEBot
from discordbot.bot_enums import ActivityTypes
from discordbot.embedmanager import EmbedManager

from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.interactions import UserInteractions
from mongo.bsepoints.points import UserPoints
from mongo.bsepoints.stickers import ServerStickers
from mongo.bseticketedevents import RevolutionEvent


class BaseEvent(object):
    """
    This is a BaseEvent class that all events will inherit from.

    Basically just sets up all the vars that events will need and rely on.
    """
    def __init__(
        self,
        client: BSEBot,
        guild_ids: list,
        logger: logging.Logger
    ):
        """
        Constructor that initialises references DB Collections and various variables
        :param client:
        :param guild_ids:
        :param logger:
        """
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.server_emojis = ServerEmojis()
        self.server_stickers = ServerStickers()
        self.revolutions = RevolutionEvent()
        self.interactions = UserInteractions()
        self.guilds = Guilds()
        self.client = client
        self.guild_ids = guild_ids
        self.embed_manager = EmbedManager(logger)
        self.logger = logger

    def _add_event_type_to_activity_history(
            self, user: discord.Member, guild_id: int, _type: ActivityTypes, **params
    ) -> None:
        """

        :param user:
        :param guild_id:
        :param _type:
        :param params:
        :return:
        """

        self.logger.info(f"{_type.name} triggered by {user.name} with {params}")

        doc = {
            "type": _type,
            "timestamp": datetime.datetime.now(),
        }

        if params:
            doc["comment"] = f"Command parameters: {', '.join([f'{key}: {params[key]}' for key in params])}"

        self.user_points.append_to_activity_history(user.id, guild_id, doc)
