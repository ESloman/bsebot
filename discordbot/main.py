"""This file is our "main" file and the entrypoint for our Discord bot.

It creates the necessary BSEBot class using our discord token and also an instance of our
CommandManager class.

This file also contains a _create_logger method that creates a logging.Logger object for us to use throughout the
rest of the codebase.
"""

import logging
import os
import sys
from pathlib import Path

import discord
import dotenv
from slomanlogger import SlomanLogger

from discordbot import __version__
from discordbot.bsebot import BSEBot
from discordbot.commandmanager import CommandManager

TOKEN: str | None = None
DEBUG_MODE: bool = False


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

    token = dotenv.get_key(".env", "DISCORD_TOKEN")
    if not token:
        token = os.environ.get("DISCORD_TOKEN")
    TOKEN = token

    debug = dotenv.get_key(".env", "DEBUG_MODE")
    if not debug:
        debug = os.environ.get("DEBUG_MODE")
    DEBUG_MODE = bool(int(debug)) if debug is not None else False

    output_path: Path = Path(Path.home(), "bsebotlogs", "bsebot.log")
    logger = SlomanLogger("bsebot", logging.DEBUG if DEBUG_MODE else logging.INFO, output_file=output_path)

    logger.info("Logging mode set to %s", logging.DEBUG if DEBUG_MODE else logging.INFO)

    logger.info("Version is: %s", __version__)

    if TOKEN is None:
        logger.error("Token isn't set - can't authenticate with Discord. Exiting.")
        sys.exit(-1)

    logger.info("Debug mode is %s.", "enabled" if DEBUG_MODE else "disabled")

    # load giphy token
    if not os.environ.get("GIPHY_TOKEN"):
        giphy_token = dotenv.get_key(".env", "GIPHY_TOKEN")
        if giphy_token:
            os.environ["GIPHY_TOKEN"] = giphy_token
            logger.verbose("Set giphy token var from .env file")
        else:
            logger.warning("No giphy token set.")

    intents = discord.Intents.all()
    intents.presences = False
    intents.typing = False

    listening_activity = discord.Activity(
        name="conversations",
        type=discord.ActivityType.listening,
        details="Waiting for commands!",
    )

    cli = BSEBot(intents=intents, activity=listening_activity, max_messages=5000)
    com = CommandManager(cli)
    cli.run(TOKEN)
