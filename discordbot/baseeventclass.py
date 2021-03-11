import datetime
import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserLoans, UserPoints
from mongo.bseticketedevents import RevolutionEvent


class BaseEvent(object):
    """
    This is a BaseEvent class that all events will inherit from.

    Basically just sets up all the vars that events will need and rely on.
    """
    def __init__(self,
                 client: discord.Client,
                 guild_ids: list,
                 logger: logging.Logger,
                 beta_mode: bool = False):
        """
        Constructor that initialises references DB Collections and various variables
        :param client:
        :param guild_ids:
        :param logger:
        :param beta_mode:
        """
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.user_loans = UserLoans()
        self.revolutions = RevolutionEvent()
        self.client = client
        self.guild_ids = guild_ids
        self.beta_mode = beta_mode
        self.embed_manager = EmbedManager(logger)
        self.logger = logger

    def _add_event_type_to_activity_history(
            self, user: discord.Member, guild_id: int, _type: ActivityTypes, **params) -> None:
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
