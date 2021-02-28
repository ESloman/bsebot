import logging

import discord

from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserLoans, UserPoints


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
        self.client = client
        self.guild_ids = guild_ids
        self.beta_mode = beta_mode
        self.embed_manager = EmbedManager(logger)
        self.logger = logger
