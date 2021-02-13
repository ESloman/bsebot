import os

from typing import List, Dict, Union

import discord
import discord_slash
import dotenv
import inflect
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from discordbot.clienteventclasses import OnReadyEvent, OnReactionAdd
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserPoints, UserBets


class CommandManager(object):
    def __init__(self, client, guilds, beta_mode=False):
        self.client = client
        self.slash = SlashCommand(client, auto_register=True, auto_delete=True)
        self.beta_mode = beta_mode

        self.embeds = EmbedManager()

        self.user_points = UserPoints()
        self.user_bets = UserBets(guilds)

        self.on_ready = OnReadyEvent(client, guilds, self.beta_mode)
        self.on_reaction_add = OnReactionAdd(guilds, self.beta_mode)

        self.register_client_events()
        self.register_slash_commands(guilds)

    def register_client_events(self):
        @self.client.event
        async def on_ready():
            self.on_ready.on_ready()

        @self.client.event
        async def on_reaction_add(reaction, user):
            await self.on_reaction_add.handle_reaction_event(reaction, user)

    def register_slash_commands(self, guilds):
        """
        Method for registering all the commands in one place.
        Most of these functions should call on the other classes to do the heavy lifting.
        :param guilds:
        :return:
        """
        @self.slash.slash(name="ping", guild_ids=guilds)
        async def ping(ctx: discord_slash.model.SlashContext):
            await ctx.send(content=f"Pong! ({self.client.latency * 1000}ms)")

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="view",
            description="View your total BSEddies",
            guild_ids=guilds)
        async def bseddies(ctx: discord_slash.model.SlashContext):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
            await ctx.send(content=f"You have **{points}** :money_with_wings:`BSEDDIES`:money_with_wings:!",
                           hidden=True)

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="leaderboard",
            description="View the BSEddie leaderboard.",
            guild_ids=guilds)
        async def leaderboard(ctx: discord_slash.model.SlashContext):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            embed = self.embeds.get_leaderboard_embed(ctx.guild, 5)
            message = await ctx.channel.send(embed=embed, delete_after=300)
            await message.add_reaction(u"▶️")

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="gift",
            description="Gift some of your eddies to a friend",
            options=[
                manage_commands.create_option(
                    name="friend",
                    description="The friend to gift the eddies to.",
                    option_type=6,
                    required=True
                ),
                manage_commands.create_option(
                    name="amount",
                    description="The amount to gift to a friend.",
                    option_type=4,
                    required=True
                )
            ],
            guild_ids=guilds)
        async def gift_eddies(ctx: discord_slash.model.SlashContext, friend: discord.User, amount: int):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            if amount < 0:
                msg = f"You can't _\"gift\"_ someone negative points."
                await ctx.send(content=msg, hidden=True)
                return

            points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
            if points < amount:
                msg = f"You have insufficient points to perform that action."
                await ctx.send(content=msg, hidden=True)
                return

            if friend.id == ctx.author.id:
                msg = f"You can't gift yourself points."
                await ctx.send(content=msg, hidden=True)
                return

            if not friend.dm_channel:
                await friend.create_dm()
            try:
                msg = f"**{ctx.author.name}** just gifted you `{amount}` eddies!!"
                await friend.send(content=msg)
            except discord.errors.Forbidden:
                pass

            self.user_points.decrement_points(ctx.author.id, ctx.guild.id, amount)
            self.user_points.increment_points(friend.id, ctx.guild.id, amount)

            await ctx.send(content=f"Eddies transferred to `{friend.name}`!", hidden=True)

        @self.slash.subcommand(
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
            ],
            guild_ids=guilds
        )
        async def handle_bet_creation(ctx, bet_title: str):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            option_dict = {"✅": {"val": "succeed", "text": "yes"}, "❌": {"val": "fail", "text": "no"}}

            bet = self.user_bets.create_new_bet(
                ctx.guild.id,
                ctx.author.id,
                bet_title,
                options=["succeed", "fail"],
                option_dict=option_dict,
            )

            embed = self.embeds.get_bet_embed(ctx.guild, bet["bet_id"], bet)

            member = ctx.guild.get_member(ctx.author.id)
            # embed.set_author(name=member.name)

            content = f"Bet created by {member.mention}"

            # await ctx.send(content=f"Bet created: {bet_title}", hidden=True)
            message = await ctx.channel.send(content=content, embed=embed)

            self.user_bets.update(
                {"_id": bet["_id"]},
                {"$set": {"message_id": message.id, "channel_id": message.channel.id}}
            )

            for emoji in option_dict:
                await message.add_reaction(emoji)

        @self.slash.subcommand(
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
            ],
            guild_ids=guilds
        )
        async def do_a_bet(ctx: discord_slash.model.SlashContext, bet_id: str, amount: int, emoji: str):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            guild = ctx.guild  # type: discord.Guild
            bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

            if not bet["active"]:
                msg = f"Your reaction on **Bet {bet_id}** failed as the bet is closed for new bets."
                await ctx.send(content=msg, hidden=True)
                return

            if emoji not in bet["option_dict"]:
                msg = f"Your reaction on **Bet {bet_id}** failed as that reaction isn't a valid outcome."
                await ctx.send(content=msg, hidden=True)
                return

            success = self.user_bets.add_better_to_bet(bet_id, guild.id, ctx.author.id, emoji, amount)
            if not success["success"]:
                msg = f"Your reaction on **Bet {bet_id}** failed cos __{success['reason']}__?"
                await ctx.send(content=msg, hidden=True)
                return False

            bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
            channel = guild.get_channel(bet["channel_id"])
            message = channel.get_partial_message(bet["message_id"])
            embed = self.embeds.get_bet_embed(guild, bet_id, bet)
            await message.edit(embed=embed)

        @self.slash.subcommand(
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
            ],
            guild_ids=guilds
        )
        async def close_a_bet(ctx: discord_slash.model.SlashContext, bet_id: str, emoji: str):
            if ctx.guild.id not in guilds:
                return

            if self.beta_mode and ctx.channel.id != 809773876078575636:
                msg = f"These features are in BETA mode and this isn't a BETA channel."
                await ctx.send(content=msg, hidden=True)
                return

            guild = ctx.guild  # type: discord.Guild
            bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

            if not bet["active"]:
                msg = f"You cannot close a bet that is already closed."
                await ctx.send(content=msg, hidden=True)
                return

            if bet["user"] != ctx.author.id:
                msg = f"You cannot close a bet that isn't yours."
                await ctx.send(content=msg, hidden=True)
                return

            if emoji not in bet["option_dict"]:
                msg = f"{emoji} isn't a valid outcome so the bet can't be closed."
                await ctx.send(content=msg, hidden=True)
                return

            success = self.user_bets.close_a_bet(bet_id, guild.id, emoji)

            desc = f"**{bet['title']}**\n{emoji} won!\n\n"

            for better in success:
                desc += f"\n- {guild.get_member(int(better)).name} won `{success[better]}` eddies!"

            channel = guild.get_channel(bet["channel_id"])
            message = channel.get_partial_message(bet["message_id"])
            await message.edit(content=desc, embed=None)
