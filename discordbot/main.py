import os

from typing import List, Dict, Union

import discord
import discord_slash
import dotenv
import inflect
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from mongo.bsepoints import UserPoints

TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")

IDS = [291508460519161856]

intents = discord.Intents.all()
p = inflect.engine()

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, auto_register=True, auto_delete=True)

USERPOINTS = UserPoints()


@client.event
async def on_ready():
    print("Checking guilds for members")
    for guild in client.guilds:  # type: List[discord.Guild]
        print(f"Checking guild: {guild.id} - {guild.name}")
        for member in guild.members:
            if not member.bot:
                print(f"Checking {member.id} - {member.name}")
                user = USERPOINTS.find_user(member.id, guild.id)
                if not user:
                    USERPOINTS.create_user(member.id, guild.id)
                    print(f"Creating new user entry for {member.id} - {member.name} for {guild.id} - {guild.name}")
    print("Finished member check.")


@client.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return
    if reaction.message.embeds and reaction.message.embeds[0].title == "BSEddies Leaderboard":
        embed = _get_leaderboard_embed(reaction.message.guild, None)
        await reaction.message.edit(embed=embed)


@slash.slash(name="ping", guild_ids=IDS)
async def _ping(ctx: discord_slash.model.SlashContext):
    await ctx.send(content=f"Pong! ({client.latency * 1000}ms)")


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    name="view",
    description="View your total BSEddies",
    guild_ids=IDS)
async def _bseddies(ctx: discord_slash.model.SlashContext):
    points = USERPOINTS.get_user_points(ctx.author.id, ctx.guild.id)
    await ctx.send(content=f"You have **{points}** :money_with_wings:`BSEDDIES`:money_with_wings:!", hidden=True)


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    name="leaderboard",
    description="View the BSEddie leaderboard.",
    guild_ids=IDS)
async def _leaderboard(ctx: discord_slash.model.SlashContext):
    embed = _get_leaderboard_embed(ctx.guild, 5)
    message = await ctx.channel.send(embed=embed, delete_after=300)
    await message.add_reaction(u"▶️")


def _get_leaderboard_embed(guild: discord.Guild, number: Union[int, None]):
    users = USERPOINTS.get_all_users_for_guild(guild.id)

    for i in range(8):
        users.append({"uid": 189458414764687360, "points": 5 + i})

    users = sorted(users, key=lambda x: x["points"], reverse=True)

    embed = discord.Embed(
        title="BSEddies Leaderboard",
        color=discord.Color.green(),
        description=""
    )

    message = ""

    if number is None:
        number = len(users)
    else:
        number = number if number < len(users) else len(users)

    for user in users[:number]:
        name = guild.get_member(user["uid"]).name
        con = f":{p.number_to_words(users.index(user) + 1)}: {name}  :  {user['points']}"
        if message:
            message += "\n"
        message += con

    if number < 6:
        message += "\n\n :arrow_forward: for longer list"

    embed.description = message

    return embed


if __name__ == "__main__":
    client.run(TOKEN)
