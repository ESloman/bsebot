
"""
This file is our "main" file and the entrypoint for our Discord bot.
It creates the necessary BSEBot class using our discord token and also an instance of our
CommandManager class.

This file also contains a _create_logger method that creates a logging.Logger object for us to use throughout the
rest of the codebase.
"""

import logging
import os

import discord

try:
    import dotenv
    DOTENV = True
except ImportError:
    DOTENV = False

from bsebot import BSEBot
from discordbot.commandmanager import CommandManager
from discordbot.constants import SLOMAN_SERVER_ID, BSE_SERVER_ID
from discordbot import utilities
from mongo.bsepoints.bets import UserBets


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

    if DOTENV:
        TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")
        DEBUG_MODE = dotenv.get_key(".env", "DEBUG_MODE")
        GIPHY_TOKEN = dotenv.get_key(".env", "GIPHY_API_KEY")
        GITHUB_TOKEN = dotenv.get_key(".env", "GITHUB_API_KEY")
    else:
        TOKEN = None
        DEBUG_MODE = None
        GIPHY_TOKEN = None
        GITHUB_TOKEN = None

    if not TOKEN:
        TOKEN = os.environ.get("DISCORD_TOKEN")
    if not DEBUG_MODE:
        DEBUG_MODE = os.environ.get("DEBUG_MODE")
    if not GIPHY_TOKEN:
        GIPHY_TOKEN = os.environ.get("GIPHY_TOKEN")
    if not GITHUB_TOKEN:
        GITHUB_TOKEN = os.environ.get("GITHUB_API_KEY")

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

    logger = utilities.create_logger(logging.DEBUG if DEBUG_MODE else logging.INFO)

    intents = discord.Intents.all()

    intents.presences = False
    intents.typing = False

    listening_activity = discord.Activity(
        name="conversations",
        type=discord.ActivityType.listening,
        details="Waiting for commands!"
    )

    cli = BSEBot(
        intents=intents,
        activity=listening_activity,
        max_messages=5000
    )

    com = CommandManager(cli, IDS, logger, giphy_token=GIPHY_TOKEN, github_token=GITHUB_TOKEN)

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
