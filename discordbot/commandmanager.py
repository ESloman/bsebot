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
from discordbot.clienteventclasses import OnReadyEvent, OnReactionAdd, OnMessage, OnMemberJoin
from discordbot.eddiegainmessageclass import EddieGainMessager
from discordbot.eddiekingtask import BSEddiesKing
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses import BSEddiesActive, BSEddiesGift, BSEddiesLeaderboard, BSEddiesView
from discordbot.slashcommandeventclasses import BSEddiesCreateBet, BSEddiesCloseBet, BSEddiesPlaceEvent
from discordbot.slashcommandeventclasses import BSEddiesPending
from mongo.bsepoints import UserPoints, UserBets


class CommandManager(object):
    """
    Class for registering all the client events and slash commands
    Needs to be initialised with a client and a list of guild IDS
    """

    def __init__(self, client: discord.Client, guilds, logger, beta_mode=False, debug_mode=False):
        self.client = client
        self.slash = SlashCommand(client, sync_commands=True)
        self.beta_mode = beta_mode
        self.guilds = guilds
        self.logger = logger

        self.embeds = EmbedManager(self.logger)

        # mongo interaction classes
        self.user_points = UserPoints()
        self.user_bets = UserBets(guilds)

        # client event classes
        self.on_ready = OnReadyEvent(client, guilds, self.logger, self.beta_mode)
        self.on_reaction_add = OnReactionAdd(client, guilds, self.logger, self.beta_mode)
        self.on_message = OnMessage(client, guilds, self.logger, self.beta_mode)
        self.on_member_join = OnMemberJoin(client, guilds, self.logger, self.beta_mode)

        # slash command classes
        self.bseddies_active = BSEddiesActive(client, guilds, self.logger, self.beta_mode)
        self.bseddies_create = BSEddiesCreateBet(client, guilds, self.logger, self.beta_mode)
        self.bseddies_gift = BSEddiesGift(client, guilds, self.logger, self.beta_mode)
        self.bseddies_view = BSEddiesView(client, guilds, self.logger, self.beta_mode)
        self.bseddies_leaderboard = BSEddiesLeaderboard(client, guilds, self.logger, self.beta_mode)
        self.bseddies_close = BSEddiesCloseBet(client, guilds, self.logger, self.beta_mode)
        self.bseddies_place = BSEddiesPlaceEvent(client, guilds, self.logger, self.beta_mode)
        self.bseddies_pending = BSEddiesPending(client, guilds, self.logger, self.beta_mode)

        # tasks
        self.bet_closer_task = BetCloser(self.client, guilds, self.logger)
        self.eddie_gain_message_task = EddieGainMessager(self.client, guilds, self.logger)
        self.eddie_king_task = BSEddiesKing(self.client, guilds, self.logger)

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
            """
            Event that handles when we're 'ready'
            :return:
            """
            await self.on_ready.on_ready()

        @self.client.event
        async def on_member_join(member: discord.Member):
            """
            Event that's called when a new member joins the guild.
            :param member:
            :return:
            """
            self.on_member_join.on_join(member)

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
            if message.author.bot:
                return
            await self.on_message.message_received(message)

    def _register_slash_commands(self, guilds):
        """l
        Method for registering all the commands in one place.
        Most of these functions should call on the other classes to do the heavy lifting.
        :param guilds:
        :return:
        """

        @self.slash.slash(name="ping", guild_ids=guilds)
        async def ping(ctx):
            """
            Just a simple ping between discord and the server. More of a test method.
            :param ctx:
            :return:
            """
            await ctx.send(content=f"Pong! ({self.client.latency * 1000}ms)")

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="view",
            description="View your total BSEddies",
            guild_ids=guilds)
        async def bseddies(ctx: discord_slash.context.SlashContext):
            """
            Slash command that allows the user to see how many BSEddies they have.
            :param ctx:
            :return:
            """
            await self.bseddies_view.view(ctx)

        @self.slash.subcommand(
            base="bseddies",
            base_description="View your BSEddies, create bets and resolve bets",
            name="leaderboard",
            description="View the BSEddie leaderboard.",
            guild_ids=guilds)
        async def leaderboard(ctx):
            """
            Slash command that allows the user to see the BSEddies leaderboard.
            :param ctx:
            :return:
            """
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
            name="pending",
            description="View all the unresolved bets you have betted on.",
            guild_ids=guilds)
        async def pending_bets(ctx: discord_slash.context.SlashContext):
            """
            Slash commands lists all the pending bets in the system for the user.
            :param ctx:
            :return:
            """
            await self.bseddies_pending.pending(ctx)

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
            """
            A slash command that allows users to gift eddies to their friends.

            It was two main arguments:
                - FRIEND: The user in the server to gift BSEddies to
                - AMOUNT: The amount of BSEddies to gift

            :param ctx:
            :param friend:
            :param amount:
            :return:
            """
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
                    name="outcome_one",
                    description="Outcome number 1 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_two",
                    description="Outcome number 2 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_three",
                    description="Outcome number 3 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="outcome_four",
                    description="Outcome number 4 name",
                    option_type=3,
                    required=False
                ),
                manage_commands.create_option(
                    name="timeout",
                    description=("How long should betting be open for? Must be DIGITS + (s|m|h|d). "
                                 "Examples: 15m, 2d, 6h, etc"),
                    option_type=3,
                    required=False
                )
            ],
            guild_ids=guilds
        )
        async def handle_bet_creation(
                ctx: discord_slash.context.SlashContext,
                bet_title: str,
                outcome_one=None,
                outcome_two=None,
                outcome_three=None,
                outcome_four=None,
                timeout=None,
        ):
            """
            This is the command for bet creation. There's quite a few optional arguments here but it's
            relatively simple.

            The only required argument is BET_TITLE:
                - BET_TITLE: The title of the bet.

            If only provided BET_TITLE, the bet should be a yes/no style question as those will be the
            default outcomes.

            The next four optional arguments are all outcome names. These should be provided in numerical order -
            one, two, three, and lastly, four. And at least two should be provided if you want custom
            outcome names.

            The final optional outcome is TIMEOUT. This is a simple string consisting of 1-4 digits + s, m, h, or d.
            This indicates how long the bet should be "open" for.

            :param ctx:
            :param bet_title:
            :param outcome_one:
            :param outcome_two:
            :param outcome_three:
            :param outcome_four:
            :param timeout:
            :return:
            """
            await self.bseddies_create.handle_bet_creation(
                ctx, bet_title,
                outcome_one, outcome_two, outcome_three, outcome_four,
                timeout
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
            """
            This is the command that allows users to place BSEddies.  on currently active bets.

            It has 3 main arguments:
                - BET_ID : The ID of the bet
                - AMOUNT : The amount of BSEddies to bet
                - EMOJI : The result to bet on

            Users can only bet on "active" bets. IE ones that haven't timed out or ones that have results already.
            Users can't bet on a different result to one that they've already bet on.
            Users can't bet a negative amount of BSEddies.
            Users can't bet on a result that doesn't exist for that bet.

            :param ctx:
            :param bet_id:
            :param amount:
            :param emoji:
            :return:
            """
            await self.bseddies_place.place_bet(ctx, bet_id, amount, emoji)

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
            """
            This is the command that closes a bet. Closing a bet requires a result emoji.
            Once a bet is "closed" - no-one can bet on it and the winners will gain their BSEddies.

            It has 2 main arguments:
                - BET_ID : The ID of the bet
                - EMOJI : The result to that won

            :param ctx:
            :param bet_id:
            :param emoji:
            :return:
            """
            await self.bseddies_close.close_bet(ctx, bet_id, emoji)
