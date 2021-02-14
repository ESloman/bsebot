import discord
import discord_slash
import dotenv
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from discordbot.commandmanager import CommandManager
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserPoints, UserBets


if __name__ == "__main__":
    TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")
    BETA_MODE = dotenv.get_key(".env", "BETA_MODE")

    if BETA_MODE is None:
        BETA_MODE = True
    else:
        BETA_MODE = False

    if BETA_MODE is False:
        IDS = [291508460519161856]  # test IDs
    else:
        BETA_MODE = True
        IDS = [181098823228063764]  # actual IDS

    intents = discord.Intents.all()

    client = discord.Client()
    cli = commands.Bot(command_prefix="!", intents=intents)
    bot = commands.Bot(command_prefix="!", intents=intents)

    com = CommandManager(cli, IDS, beta_mode=BETA_MODE)
    embeds = EmbedManager()

    user_bets = UserBets(IDS)

    cli.run(TOKEN)
