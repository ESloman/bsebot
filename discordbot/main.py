import os

import discord
import discord_slash
import dotenv
import inflect
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from discordbot.commandmanager import CommandManager
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserPoints, UserBets

TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")

# IDS = [291508460519161856]  # test IDs
IDS = [181098823228063764]  # actual IDS

intents = discord.Intents.all()

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)


com = CommandManager(client, IDS, beta_mode=True)
embeds = EmbedManager()
slash = com.slash


USERBETS = UserBets(IDS)


if __name__ == "__main__":
    client.run(TOKEN)
