import os

from typing import List, Dict, Union

import discord
import discord_slash
import dotenv
import inflect
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from mongo.bsepoints import UserPoints, UserBets

TOKEN = dotenv.get_key(".env", "DISCORD_TOKEN")

# IDS = [291508460519161856]  # test IDs
IDS = [181098823228063764]  # actual IDS

intents = discord.Intents.all()
p = inflect.engine()

client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix="!", intents=intents)
slash = SlashCommand(client, auto_register=True, auto_delete=True)

USERPOINTS = UserPoints()
USERBETS = UserBets(IDS)


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
    if reaction.message.channel.id != 809773876078575636:
        return

    if reaction.message.embeds and reaction.message.embeds[0].title == "BSEddies Leaderboard":
        embed = _get_leaderboard_embed(reaction.message.guild, None)
        await reaction.message.edit(embed=embed)
    elif reaction.message.embeds and "Bet ID" in reaction.message.embeds[0].description:
        message = reaction.message
        embed = message.embeds[0]  # type: discord.Embed
        bet_id = embed.description.replace("Bet ID: ", "")
        bet = USERBETS.get_bet_from_id(reaction.message.guild.id, bet_id)

        if not bet["active"]:
            return

        if reaction.emoji not in bet['option_dict']:
            await reaction.remove(user)
            return
        ret = USERBETS.add_better_to_bet(bet_id, reaction.message.guild.id, user.id, reaction.emoji, 1)
        if ret["success"]:
            print("bet successful!")
            new_bet = USERBETS.get_bet_from_id(reaction.message.guild.id, bet_id)
            embed = _get_bet_embed(reaction.message.guild, bet_id, new_bet)
            await reaction.message.edit(embed=embed)
        await reaction.remove(user)

        print("Got a bet!")


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
    if ctx.channel.id != 809773876078575636:
        return
    points = USERPOINTS.get_user_points(ctx.author.id, ctx.guild.id)
    await ctx.send(content=f"You have **{points}** :money_with_wings:`BSEDDIES`:money_with_wings:!", hidden=True)


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    name="leaderboard",
    description="View the BSEddie leaderboard.",
    guild_ids=IDS)
async def _leaderboard(ctx: discord_slash.model.SlashContext):
    if ctx.channel.id != 809773876078575636:
        return
    embed = _get_leaderboard_embed(ctx.guild, 5)
    message = await ctx.channel.send(embed=embed, delete_after=300)
    await message.add_reaction(u"▶️")


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    subcommand_group="bet",
    subcommand_group_description="Create or resolve bets using BSEddies",
    name="create",
    description="Create a bet",
    options=[
        manage_commands.create_option(
            name="bet_title",
            description="What is the bet?",
            option_type=3,
            required=True
        )
    ]
)
async def _handle_bet_creation(ctx, bet_title: str):
    if ctx.channel.id != 809773876078575636:
        return
    option_dict = {"✅": {"val": "succeed", "text": "yes"}, "❌": {"val": "fail", "text": "no"}}

    bet = USERBETS.create_new_bet(
        ctx.guild.id,
        ctx.author.id,
        bet_title,
        options=["succeed", "fail"],
        option_dict=option_dict,
    )

    embed = _get_bet_embed(ctx.guild, bet["bet_id"], bet)

    member = ctx.guild.get_member(ctx.author.id)
    # embed.set_author(name=member.name)

    content = f"Bet created by {member.mention}"

    # await ctx.send(content=f"Bet created: {bet_title}", hidden=True)
    message = await ctx.channel.send(content=content, embed=embed)

    USERBETS.update({"_id": bet["_id"]}, {"$set": {"message_id": message.id, "channel_id": message.channel.id}})

    for emoji in option_dict:
        await message.add_reaction(emoji)


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    subcommand_group="bet",
    subcommand_group_description="Create, resolve, or place bets using BSEddies",
    name="place",
    description="Place a bet",
    options=[
        manage_commands.create_option(
            name="bet_id",
            description="Bet ID to place a bet on",
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name="amount",
            description="Amount of BSEddies to bet",
            option_type=4,
            required=True
        ),
        manage_commands.create_option(
            name="emoji",
            description="Which result to bet on",
            option_type=3,
            required=True
        ),
    ]
)
async def _do_a_bet(ctx, bet_id: str, amount: int, emoji: str):
    if ctx.channel.id != 809773876078575636:
        return

    guild = ctx.guild  # type: discord.Guild
    bet = USERBETS.get_bet_from_id(guild.id, bet_id)

    if not bet["active"]:
        return

    if emoji not in bet["option_dict"]:
        return

    success = USERBETS.add_better_to_bet(bet_id, guild.id, ctx.author.id, emoji, amount)
    if not success["success"]:
        return False

    bet = USERBETS.get_bet_from_id(guild.id, bet_id)
    channel = guild.get_channel(bet["channel_id"])
    message = channel.get_partial_message(bet["message_id"])
    embed = _get_bet_embed(guild, bet_id, bet)
    await message.edit(embed=embed)


@slash.subcommand(
    base="bseddies",
    base_description="View your BSEddies, create bets and resolve bets",
    subcommand_group="bet",
    subcommand_group_description="Create, resolve, or place bets using BSEddies",
    name="close",
    description="Close a bet by providing a result and award those SWEET EDDIES.",
    options=[
        manage_commands.create_option(
            name="bet_id",
            description="Bet ID to close.",
            option_type=3,
            required=True
        ),
        manage_commands.create_option(
            name="emoji",
            description="Which result WON",
            option_type=3,
            required=True
        ),
    ]
)
async def _close_a_bet(ctx, bet_id: str, emoji: str):
    if ctx.channel.id != 809773876078575636:
        return

    guild = ctx.guild  # type: discord.Guild
    bet = USERBETS.get_bet_from_id(guild.id, bet_id)

    if bet["user"] != ctx.author.id:
        return

    if emoji not in bet["option_dict"]:
        return

    success = USERBETS.close_a_bet(bet_id, guild.id, emoji)

    desc = f"**{bet['title']}**\n{emoji} won!\n\n"

    for better in success:
        desc += f"\n- {guild.get_member(int(better)).name} won `{success[better]}` eddies!"

    channel = guild.get_channel(bet["channel_id"])
    message = channel.get_partial_message(bet["message_id"])
    await message.edit(content=desc, embed=None)


def _get_bet_embed(guild: discord.Guild, bet_id, bet: dict):
    embed = discord.Embed(
        title=bet["title"],
        description=f"Bet ID: {bet_id}",
        color=discord.Color.blue(),
    )

    for option in bet["option_dict"]:
        betters = [bet['betters'][b] for b in bet['betters'] if bet['betters'][b]["emoji"] == option]
        if betters:
            val = ""
            for better in sorted(betters, key=lambda b: b["points"], reverse=True):
                if val:
                    val += "\n"
                better_info = guild.get_member(better["user_id"])
                val += f"- {better_info.name} - {better['points']}"
        else:
            val = "No-one has bet on this option yet."
        embed.add_field(
            name=f"{option} - {bet['option_dict'][option]['val']}",
            value=val,
            inline=False
        )
    return embed


def _get_leaderboard_embed(guild: discord.Guild, number: Union[int, None]):
    users = USERPOINTS.get_all_users_for_guild(guild.id)

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
