import os

from typing import List, Dict, Union

import discord
import discord_slash
import dotenv
import inflect
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils import manage_commands

from discordbot.betcloser import BetCloser
from discordbot.clienteventclasses import OnReadyEvent, OnReactionAdd
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses import BSEddiesActive, BSEddiesGift, BSEddiesLeaderboard, BSEddiesView
from discordbot.slashcommandeventclasses import BSEddiesCreateBet, BSEddiesCloseBet
from mongo.bsepoints import UserPoints, UserBets


class CommandManager(object):
    """
    Class for registering all the client events and slash commands
    Needs to be initialised with a client and a list of guild IDS
    """

    def __init__(self, client: discord.Client, guilds, beta_mode=False):
        self.client = client
        self.slash = SlashCommand(client, sync_commands=True)
        self.beta_mode = beta_mode
        self.guilds = guilds

        self.embeds = EmbedManager()

        # mongo interaction classes
        self.user_points = UserPoints()
        self.user_bets = UserBets(guilds)

        # client event classes
        self.on_ready = OnReadyEvent(client, guilds, self.beta_mode)
        self.on_reaction_add = OnReactionAdd(client, guilds, self.beta_mode)

        # slash command classes
        self.bseddies_active = BSEddiesActive(client, guilds, self.beta_mode)
        self.bseddies_create = BSEddiesCreateBet(client, guilds, self.beta_mode)
        self.bseddies_gift = BSEddiesGift(client, guilds, self.beta_mode)
        self.bseddies_view = BSEddiesView(client, guilds, self.beta_mode)
        self.bseddies_leaderboard = BSEddiesLeaderboard(client, guilds, self.beta_mode)
        self.bseddies_close = BSEddiesCloseBet(client, guilds, self.beta_mode)

        # tasks
        self.bet_closer_task = BetCloser(self.client, guilds)

        # call the methods that register the events we're listening for
        self._register_client_events()
        self._register_slash_commands(guilds)

    # noinspection PyProtectedMember
    def __get_cached_messages_list(self):
        """
        Method for getting a list of cached message IDs
        :return:
        """
        deque = self.client.cached_messages._SequenceProxy__proxied
        cached = [d.id for d in deque]
        return cached

    def _register_client_events(self):
        @self.client.event
        async def on_ready():
            self.on_ready.on_ready()

        @self.client.event
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
            """
            This event catches EVERY reaction event on every message in the server.
            However, any operations we want to perform are a bit slower as we need to 'fetch' the message
            before we have all the data we have. BUT, we need to handle reactions to all messages as a user may
            react to an older message that isn't in the cache and we can't just not do anything.

            If the message is in the cache - then this event will fire and so will on_reaction_add. To prevent that,
            and to keep on_reaction_add for cached messages and be faster, we check if the message_id is already
            in the cache. If it is, then we can safely ignore it here. Otherwise we need to handle it.
            :param payload:
            :return:
            """

            cached_messages = self.__get_cached_messages_list()
            if payload.message_id in cached_messages:
                # message id is already in the cache
                return

            guild = self.client.get_guild(payload.guild_id)  # type: discord.Guild
            user = guild.get_member(payload.user_id)  # type: discord.User

            if user.bot:
                return

            channel = guild.get_channel(payload.channel_id)  # type: discord.TextChannel
            partial_message = channel.get_partial_message(payload.message_id)  # type: discord.PartialMessage
            message = await partial_message.fetch()  # type: discord.Message

            await self.on_reaction_add.handle_reaction_event(message, guild, channel, payload.emoji.name, user)

        @self.client.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
            """
            This event is triggered when anyone 'reacts' to a message in a guild that the bot is in - even it's own
            reactions. However, this only triggers for messages that the bot has in it's cache - reactions to older
            messages will only trigger a 'on_raw_reaction_add' event.

            Here, we simply hand it off to another class to deal with.
            :param reaction:
            :param user:
            :return:
            """
            await self.on_reaction_add.handle_reaction_event(
                reaction.message,
                reaction.message.guild,
                reaction.message.channel,
                reaction.emoji,
                user
            )

        @self.client.event
        async def on_message(message: discord.Message):
            """
            This is the 'message' event. Whenever a message is sent in a guild that the bot is listening for -
            we will enact this code. Here, we simply hand it off to another class to deal with.
            :param message:
            :return:
            """
            pass

    def _register_slash_commands(self, guilds):
        """
        Method for registering all the commands in one place.
        Most of these functions should call on the other classes to do the heavy lifting.
        :param guilds:
        :return:
        """

        @self.slash.slash(name="ping", guild_ids=guilds)
        async def ping(ctx):
            await ctx.send(content=f"Pong! ({self.client.latency * 1000}ms)")

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="view",
            description="View your total BSEddies",
            guild_ids=guilds)
        async def bseddies(ctx: discord_slash.context.SlashContext):
            await self.bseddies_view.view(ctx)

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="leaderboard",
            description="View the BSEddie leaderboard.",
            guild_ids=guilds)
        async def leaderboard(ctx):
            await self.bseddies_leaderboard.leaderboard(ctx)

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="active",
            description="View all the active bets in the server.",
            guild_ids=guilds)
        async def active_bets(ctx: discord_slash.context.SlashContext):
            """
            Slash commands lists all the active bets in the system.
            :param ctx:
            :return:
            """
            await self.bseddies_active.active(ctx)

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
        async def gift_eddies(ctx: discord_slash.context.SlashContext, friend: discord.User, amount: int):
            await self.bseddies_gift.gift_eddies(ctx, friend, amount)

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
                ),
                manage_commands.create_option(
                    name="outcome_one_name",
                    description="Outcome number 1 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_two_name",
                    description="Outcome number 2 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_three_name",
                    description="Outcome number 3 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_four_name",
                    description="Outcome number 4 name",
                    option_type=3,
                    required=False
                )
            ],
            guild_ids=guilds
        )
        async def handle_bet_creation(
                ctx: discord_slash.context.SlashContext,
                bet_title: str,
                outcome_one_name=None,
                outcome_two_name=None,
                outcome_three_name=None,
                outcome_four_name=None,
        ):
            """
            Catching discord slash for bet creation.
            :param ctx:
            :param bet_title:
            :param outcome_one_name:
            :param outcome_two_name:
            :param outcome_three_name:
            :param outcome_four_name:
            :return:
            """
            await self.bseddies_create.handle_bet_creation(
                ctx, bet_title, outcome_one_name, outcome_two_name, outcome_three_name, outcome_four_name
            )

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
        async def do_a_bet(ctx: discord_slash.context.SlashContext, bet_id: str, amount: int, emoji: str):
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

            emoji = emoji.strip()

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
        async def close_a_bet(ctx: discord_slash.context.SlashContext, bet_id: str, emoji: str):
            await self.bseddies_close.close_bet(ctx, bet_id, emoji)
