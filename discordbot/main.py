
"""
This file is our "main" file and the entrypoint for our Discord bot.
It creates the necessary discord.Bot class using our discord token and also an instance of our
CommandManager class.

This file also contains a _create_logger method that creates a logging.Logger object for us to use throughout the
rest of the codebase.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

import discord
import dotenv

from discordbot.commandmanager import CommandManager
from discordbot.constants import SLOMAN_SERVER_ID, BSE_SERVER_ID
from mongo.bsepoints import UserBets


def _create_logger() -> logging.Logger:
    """
    Creates a simple logger to use throughout the bot
    :return: Logger object
    """
    fol = os.path.join(os.path.expanduser("~"), "bsebotlogs")
    if not os.path.exists(fol):
        os.makedirs(fol)

    _logger = logging.getLogger("bsebot")
    _logger.setLevel(logging.DEBUG)

    formatting = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(formatting)

    # this makes sure we're logging to the standard output too
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)

    # this makes sure we're logging to a file
    file_handler = RotatingFileHandler(
        os.path.join(fol, "bsebot.log"), maxBytes=10485760, backupCount=1
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(stream_handler)
    _logger.addHandler(file_handler)

    return _logger


if __name__ == "__main__":
    """
    This is our primary entry point for getting the bot start.

    We expect a '.env' file to be located in the same directory that contains our DISCORD_TOKEN and also whether or not
    we're in DEBUG_MODE.

    We start by getting those values from the .env file and exit if we don't have a DISCORD_TOKEN.
    We then work out which SERVER_IDs to use based on whether or not we're in DEBUG_MODE.

    We then create the logger object and initialise our discord client.
    Then, we use the client to create an instance of CommandManager - this class registers all the events we're
    listening for.

    Finally, we start the asyncio loop and start listening for events.
    """

    TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")
    DEBUG_MODE = dotenv.get_key(".env", "DEBUG_MODE")
    GIPHY_TOKEN = dotenv.get_key(".env", "GIPHY_API_KEY")

    if TOKEN is None:
        exit(-1)

    if DEBUG_MODE is None:
        DEBUG_MODE = False
    else:
        DEBUG_MODE = bool(int(DEBUG_MODE))

    if DEBUG_MODE is True:
        IDS = [SLOMAN_SERVER_ID]  # test IDs
    else:
        IDS = [BSE_SERVER_ID]  # actual IDS

    logger = _create_logger()

    intents = discord.Intents.all()

    intents.presences = False
    intents.typing = False

    listening_activity = discord.Activity(
        name="conversations",
        state="Listening",
        type=discord.ActivityType.listening,
        details="Waiting for commands!"
    )

    cli = discord.Bot(
        debug_guilds=IDS,
        intents=intents,
        activity=listening_activity,
        auto_sync_commands=False,
        max_messages=5000
    )

    com = CommandManager(cli, IDS, logger, giphy_token=GIPHY_TOKEN)

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
