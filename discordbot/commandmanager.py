"""
This file contains our class that registers all the events we listen to and do things with
"""

import logging

import discord
from apis.giphyapi import GiphyAPI
from mongo.bsepoints import UserBets, UserPoints

from discordbot.clienteventclasses import OnDirectMessage, OnEmojiCreate, OnMemberJoin, OnMemberLeave
from discordbot.clienteventclasses import OnMessage, OnReactionAdd, OnReadyEvent, OnStickerCreate
from discordbot.clienteventclasses import OnThreadCreate, OnThreadUpdate

from discordbot.constants import BSE_SERVER_ID
from discordbot.embedmanager import EmbedManager
from discordbot.modals import BSEddiesBetCreateModal
from discordbot.slashcommandeventclasses import BSEddiesActive, BSEddiesAdminGive, BSEddiesAutoGenerate
from discordbot.slashcommandeventclasses import BSEddiesCloseBet, BSEddiesGift, BSEddiesHighScore, BSEddiesLeaderboard
from discordbot.slashcommandeventclasses import BSEddiesPending, BSEddiesPlaceBet, BSEddiesPredict, BSEddiesTaxRate
from discordbot.slashcommandeventclasses import BSEddiesTransactionHistory, BSEddiesView

# task imports
from discordbot.tasks.betcloser import BetCloser
from discordbot.tasks.dailyvallytask import AfterWorkVally
from discordbot.tasks.eddiegains import EddieGainMessager
from discordbot.tasks.eddiekingtask import BSEddiesKingTask
from discordbot.tasks.monthlyawards import MonthlyBSEddiesAwards
from discordbot.tasks.revolutiontask import BSEddiesRevolutionTask
from discordbot.tasks.threadmutetask import ThreadSpoilerTask
from discordbot.tasks.wordletask import WordleTask


class CommandManager(object):
    """
    Class for registering all the client events and slash commands
    Needs to be initialised with a client and a list of guild IDS

    Only the constructor needs to be called in this class for it to register everything.
    """

    def __init__(
        self,
        client: discord.Bot,
        guilds: list,
        logger: logging.Logger,
        giphy_token: str = None
    ) -> None:
        """
        Constructor method. This does all the work in this class and no other methods need to be called.

        We start by creating all the variables we need and some also an EmbedManager class (for creating embeds),
        and our MongoDB Collection classes for interacting with those collections in the DB.

        This is also where we create an instance of "SlashCommand". This is our main class that handles registering
        of the slash commands.

        Each "event" or "slash command" has their own "class" that handles all the actual logic for when we receive
        an event or slash command. So we create instances of these classes next.

        We have the Client Event classes all being registered and then all the Slash Command events being registered.

        After that, we have our "tasks". Tasks are COG objects that perform a task at regular intervals. We use tasks
        for a variety of different things. But essentially, each one is a class and we create an instance of each one
        here. There's no need to do anything else once we instantiate each of them.

        And finally, we call the two methods that actually register all the events and slash commands.

        :param client: discord.Client object that represents our bot
        :param guilds: list of guild IDs that we're listening on
        :param logger:  logger object for logging
        :param debug_mode: whether we're in debug mode or not
        :param giphy_token:
        """

        self.client = client
        self.guilds = guilds
        self.logger = logger
        self.giphy_token = giphy_token

        self.embeds = EmbedManager(self.logger)

        self.giphyapi = GiphyAPI(self.giphy_token)

        # mongo interaction classes
        self.user_points = UserPoints()
        self.user_bets = UserBets(guilds)

        self.__get_cached_messages_list()

        # client event classes
        self.on_ready = OnReadyEvent(client, guilds, self.logger)
        self.on_reaction_add = OnReactionAdd(client, guilds, self.logger)
        self.on_message = OnMessage(client, guilds, self.logger)
        self.on_member_join = OnMemberJoin(client, guilds, self.logger)
        self.on_member_leave = OnMemberLeave(client, guilds, self.logger)
        self.direct_message = OnDirectMessage(client, guilds, self.logger, self.giphyapi)
        self.on_thread_create = OnThreadCreate(client, guilds, self.logger)
        self.on_thread_update = OnThreadUpdate(client, guilds, self.logger)
        self.on_emoji_create = OnEmojiCreate(client, guilds, self.logger)
        self.on_sticker_create = OnStickerCreate(client, guilds, self.logger)

        # slash command classes
        self.bseddies_active = BSEddiesActive(client, guilds, self.logger)
        self.bseddies_gift = BSEddiesGift(client, guilds, self.logger)
        self.bseddies_view = BSEddiesView(client, guilds, self.logger)
        self.bseddies_leaderboard = BSEddiesLeaderboard(client, guilds, self.logger)
        self.bseddies_close = BSEddiesCloseBet(client, guilds, self.logger)
        self.bseddies_place = BSEddiesPlaceBet(client, guilds, self.logger)
        self.bseddies_pending = BSEddiesPending(client, guilds, self.logger)
        self.bseddies_transactions = BSEddiesTransactionHistory(client, guilds, self.logger)
        self.bseddies_admin_give = BSEddiesAdminGive(client, guilds, self.logger)
        self.bseddies_high_score = BSEddiesHighScore(client, guilds, self.logger)
        self.bseddies_predict = BSEddiesPredict(client, guilds, self.logger)
        self.bseddies_autogenerate = BSEddiesAutoGenerate(client, guilds, self.logger)
        self.bseddies_tax_rate = BSEddiesTaxRate(client, guilds, self.logger)

        # tasks
        self.bet_closer_task = BetCloser(self.client, guilds, self.logger, self.bseddies_place, self.bseddies_close)
        self.eddie_gain_message_task = EddieGainMessager(self.client, guilds, self.logger)
        self.eddie_king_task = BSEddiesKingTask(self.client, guilds, self.logger)
        self.revolution_task = BSEddiesRevolutionTask(self.client, guilds, self.logger, self.giphy_token)

        if BSE_SERVER_ID in self.guilds:
            self.thread_task = ThreadSpoilerTask(self.client, guilds, self.logger)
            self.vally_task = AfterWorkVally(self.client, guilds, self.logger)
            self.wordle_task = WordleTask(self.client, guilds, self.logger)
            self.monthly_awards_task = MonthlyBSEddiesAwards(self.client, guilds, self.logger)

        # call the methods that register the events we're listening for
        self._register_client_events()
        self._register_slash_commands(guilds)

    # noinspection PyProtectedMember
    def __get_cached_messages_list(self) -> list:
        """
        Method for getting a list of cached message IDs
        :return: list of cached messages
        """
        deque = self.client.cached_messages._SequenceProxy__proxied
        cached = [d.id for d in deque]
        return cached

    def _register_client_events(self) -> None:
        """
        This method registers all the 'client events'.
        Client Events are normal discord events that we can listen to.
        A full list of events can be found here: https://docs.pycord.dev/en/stable/api.html#event-reference

        Each event must be it's own async method with a @self.client.event decorator so that it's actually
        registered. None of these methods defined here will ever be called manually by anyone. The methods are called
        by the CLIENT object and that will pass in all the required parameters.

        Additionally, the method is called automatically from this class' constructor and shouldn't be called anywhere
        else.

        :return: None
        """

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
        async def on_member_remove(member: discord.Member):
            """
            Event that's called when a member leaves the guild.
            :param member:
            :return:
            """
            self.on_member_leave.on_leave(member)

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
            user = await self.client.fetch_user(payload.user_id)  # type: discord.User

            if user.bot:
                return

            channel = guild.get_channel(payload.channel_id)  # type: discord.TextChannel
            if not channel:
                # channel is thread
                channel = guild.get_thread(payload.channel_id)
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
        async def on_thread_create(thread: discord.Thread):
            """

            :param thread:
            :return:
            """
            await self.on_thread_create.on_thread_create(thread)

        @self.client.event
        async def on_thread_update(before: discord.Thread, after: discord.Thread):
            """

            :param before:
            :param after:
            :return:
            """

            await self.on_thread_update.on_update(before, after)

        @self.client.event
        async def on_message(message: discord.Message):
            """
            This is the 'message' event. Whenever a message is sent in a guild that the bot is listening for -
            we will enact this code. Here, we simply hand it off to another class to deal with.
            :param message:
            :return:
            """

            if message.channel.type.value == 1:
                # this means we've received a Direct message!
                # we'll have to handle this differently
                self.logger.debug(f"{message} - {message.content}")
                await self.direct_message.dm_received(message)
                return

            await self.on_message.message_received(message)

        @self.client.event
        async def on_guild_emojis_update(
            guild: discord.Guild,
            before: discord.Sequence[discord.Emoji],
            after: discord.Sequence[discord.Emoji]
        ) -> None:
            """
            For updating our internal list of emojis

            Args:
                guild (discord.Guild): the Guild object
                before (discord.Sequence[discord.Emoji]): list of emojis before
                after (discord.Sequence[discord.Emoji]): list of emojis after
            """
            await self.on_emoji_create.on_emojis_update(guild.id, before, after)

        @self.client.event
        async def on_guild_stickers_update(
            guild: discord.Guild,
            before: discord.Sequence[discord.Sticker],
            after: discord.Sequence[discord.Sticker]
        ) -> None:
            """
            For updating our internal list of emojis

            Args:
                guild (discord.Guild): the Guild object
                before (discord.Sequence[discord.Emoji]): list of stickers before
                after (discord.Sequence[discord.Emoji]): list of stickers after
            """
            await self.on_sticker_create.on_stickers_update(guild.id, before, after)

    def _register_slash_commands(self, guilds: list) -> None:
        """
        This method registers all the 'slash commands'.
        Slash Commands are commands users can use in discord.

        Each command must be it's own async method with a relevant decorator so that it's actually
        registered. None of these methods defined here will ever be called manually by anyone. The methods are called
        by the CLIENT object and that will pass in all the required parameters.

        Additionally, the method is called automatically from this class' constructor and shouldn't be called anywhere
        else.

        :param guilds: The guild IDs to register the commands to
        :return: None
        """

        @self.client.command(description="View your total BSEddies")
        async def view(ctx: discord.ApplicationContext) -> None:
            """
            Slash command that allows the user to see how many BSEddies they have.
            :param ctx:
            :return:
            """
            await self.bseddies_view.view(ctx)

        @self.client.command(description="View the current BSEddies leaderboard")
        async def leaderboard(ctx: discord.ApplicationContext) -> None:
            """
            Slash command that allows the user to see the BSEddies leaderboard.
            :param ctx:
            :return:
            """
            await self.bseddies_leaderboard.leaderboard(ctx)

        @self.client.command(description="See your estimated salary gain for today so far")
        async def predict(ctx: discord.ApplicationContext) -> None:
            """
            Slash command that allows the user to see their predict daily salary.
            :param ctx:
            :return:
            """
            await self.bseddies_predict.predict(ctx)

        @self.client.command(description="View the BSEddies High Scores.")
        async def highscores(ctx: discord.ApplicationContext) -> None:
            """
            Slash command that allows the user to see the BSEddies high scores.
            :param ctx:
            :return:
            """
            await self.bseddies_high_score.highscore(ctx)

        @self.client.command(description="View all the active bets in the server.")
        async def active(ctx: discord.ApplicationContext) -> None:
            """
            Slash commands lists all the active bets in the system.
            :param ctx:
            :return:
            """
            await self.bseddies_active.active(ctx)

        @self.client.command(description="View all the unresolved bets you have betted on.")
        async def pending(ctx: discord.ApplicationContext) -> None:
            """
            Slash commands lists all the pending bets in the system for the user.
            :param ctx:
            :return:
            """
            await self.bseddies_pending.pending(ctx)

        @self.client.command(description="Gift some of your eddies to a friend")
        async def gift(
                ctx: discord.ApplicationContext,
                friend: discord.Option(discord.User),
                amount: discord.Option(int)) -> None:
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

        @self.client.command(description="View your transaction history.")
        async def transactions(
                ctx: discord.ApplicationContext,
                full: discord.Option(
                    bool,
                    description="Do you want the full transaction history?",  # noqa: F722
                    default=False
                ),
        ) -> None:
            """
            Slash command that allows the user to see their eddie transaction history
            :param ctx:
            :param full:
            :return:
            """
            await ctx.defer(ephemeral=True)
            await self.bseddies_transactions.transaction_history(ctx, full)

        @self.client.command(description="Create a bet")
        async def create(ctx: discord.ApplicationContext):
            modal = BSEddiesBetCreateModal(
                client=self.client,
                guilds=self.guilds,
                logger=self.logger,
                title="Create a bet"
            )
            await ctx.send_modal(modal)

        @self.client.command(description="Autogenerate bets")
        async def autogenerate(ctx: discord.ApplicationContext):
            await ctx.defer(ephemeral=True)
            await self.bseddies_autogenerate.create_auto_generate_view(ctx)

        @self.client.command(description="Place a bet")
        async def place(ctx: discord.ApplicationContext) -> None:
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
            :return:
            """
            await self.bseddies_place.create_bet_view(ctx)

        @self.client.command(description="Close a bet by providing a result and award those SWEET EDDIES.")
        async def close(ctx: discord.ApplicationContext) -> None:
            """
            This is the command that closes a bet. Closing a bet requires a result emoji.
            Once a bet is "closed" - no-one can bet on it and the winners will gain their BSEddies.

            :param ctx:
            :return:
            """
            await self.bseddies_close.create_bet_view(ctx)

        @self.client.command(description="Give a user some eddies",)
        async def admin_give(
                ctx: discord.ApplicationContext, user: discord.User, amount: int) -> None:
            """
            Slash command for an admin to give eddies for someone.
            :param ctx:
            :param user:
            :param amount:
            :return:
            """
            await self.bseddies_admin_give.admin_give(ctx, user, amount)

        @self.client.command(description="Set server eddies tax rate")
        async def taxrate(ctx: discord.ApplicationContext):
            """
            Slash command to set tax rate

            Args:
                ctx (discord.ApplicationContext): _description_
            """
            await self.bseddies_tax_rate.create_tax_view(ctx)
