import discord
import dotenv
from discord.ext import commands

from discordbot.commandmanager import CommandManager
from discordbot.constants import SLOMAN_SERVER_ID, BSE_SERVER_ID
from mongo.bsepoints import UserBets


if __name__ == "__main__":
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

    intents = discord.Intents.all()

    cli = commands.Bot(command_prefix="!", intents=intents)
    com = CommandManager(cli, IDS, beta_mode=BETA_MODE)

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
