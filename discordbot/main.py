import discord
import dotenv
import logging
import os
import sys

from discord.ext import commands
from logging.handlers import RotatingFileHandler

from discordbot.commandmanager import CommandManager
from discordbot.constants import SLOMAN_SERVER_ID, BSE_SERVER_ID
from mongo.bsepoints import UserBets


def _create_logger():
    """
    Creates a simple logger to use throughout the bot
    :return:
    """
    fol = os.path.join(os.path.expanduser("~"), "bsebotlogs")
    if not os.path.exists(fol):
        os.makedirs(fol)

    _logger = logging.getLogger("bsebot")
    _logger.setLevel(logging.DEBUG)

    formatting = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(formatting)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        os.path.join(fol, "bsebot.log"), maxBytes=10485760, backupCount=1
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(stream_handler)
    _logger.addHandler(file_handler)
    return _logger


if __name__ == "__main__":
    """
    Entry point for the bot really. Gets the token information and works out which guild we're going to use.
    Then creates the necessary classes and starts the asyncio loop.
    """

    TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")
    BETA_MODE = dotenv.get_key(".env", "BETA_MODE")

    if BETA_MODE is None:
        BETA_MODE = True
    else:
        BETA_MODE = False

    if BETA_MODE is False:
        IDS = [SLOMAN_SERVER_ID]  # test IDs
    else:
        BETA_MODE = True
        IDS = [BSE_SERVER_ID]  # actual IDS

    logger = _create_logger()

    intents = discord.Intents.all()

    cli = commands.Bot(command_prefix="!", intents=intents)
    com = CommandManager(cli, IDS, logger, beta_mode=BETA_MODE)

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
