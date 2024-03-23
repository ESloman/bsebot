"""This file is our "main" file and the entrypoint for our Discord bot.

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

import sys

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.commandmanager import CommandManager
from discordbot.constants import BSE_SERVER_ID, SLOMAN_SERVER_ID
from mongo.bsepoints.bets import UserBets

TOKEN: str | None
DEBUG_MODE: bool
GIPHY_TOKEN: str | None
GITHUB_TOKEN: str | None


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
        e_debug = dotenv.get_key(".env", "DEBUG_MODE")
        GIPHY_TOKEN = dotenv.get_key(".env", "GIPHY_API_KEY")
        GITHUB_TOKEN = dotenv.get_key(".env", "GITHUB_API_KEY")
    else:
        TOKEN = None
        e_debug = None
        GIPHY_TOKEN = None
        GITHUB_TOKEN = None

    if _token := os.environ.get("DISCORD_TOKEN"):
        TOKEN = _token
    if _debug := os.environ.get("DEBUG_MODE"):
        DEBUG_MODE = bool(int(_debug))
    if _giphy_token := os.environ.get("GIPHY_TOKEN"):
        GIPHY_TOKEN = _giphy_token
    if _github := os.environ.get("GITHUB_API_KEY"):
        GITHUB_TOKEN = _github

    DEBUG_MODE = DEBUG_MODE or (False if e_debug is None else bool(int(e_debug)))

    IDS = [SLOMAN_SERVER_ID] if DEBUG_MODE is True else [BSE_SERVER_ID]

    logger = utilities.create_logger(logging.DEBUG if DEBUG_MODE else logging.INFO)

    logger.info("Logging mode set to %s", logging.DEBUG if DEBUG_MODE else logging.INFO)

    if TOKEN is None:
        logger.error("Token isn't set - can't authenticate with Discord. Exiting.")
        sys.exit(-1)

    if DEBUG_MODE:
        logger.info("Debug mode enabled.")
    if GIPHY_TOKEN:
        logger.debug("Giphy token set.")
    if GITHUB_TOKEN:
        logger.debug("Github token set.")

    intents = discord.Intents.all()

    intents.presences = False
    intents.typing = False

    listening_activity = discord.Activity(
        name="conversations",
        type=discord.ActivityType.listening,
        details="Waiting for commands!",
    )

    cli = BSEBot(intents=intents, activity=listening_activity, max_messages=5000, logger=logger)

    com = CommandManager(cli, IDS, logger, giphy_token=GIPHY_TOKEN, github_token=GITHUB_TOKEN)

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
