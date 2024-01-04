"""Contains the CommandManager class.

The purpose of CommandManager is to have a singular place where we create all the
listeners for our client events and where we also register all our slash commands.
Each event/command has a corresponding python class that handles the primary logic - but we connect the discord events
to those classes here in this file. It does the bulk of it's work in the __init__ method.

Any new client events and slash commands will need to be added here.
"""

import contextlib
import inspect
import logging

import discord

from apis.giphyapi import GiphyAPI
from apis.github import GitHubAPI
from discordbot.bsebot import BSEBot

# client events
from discordbot.clienteventclasses.ondirectmessage import OnDirectMessage
from discordbot.clienteventclasses.onemojicreate import OnEmojiCreate
from discordbot.clienteventclasses.onmemberjoin import OnMemberJoin
from discordbot.clienteventclasses.onmemberleave import OnMemberLeave
from discordbot.clienteventclasses.onmessage import OnMessage
from discordbot.clienteventclasses.onmessageedit import OnMessageEdit
from discordbot.clienteventclasses.onreactionadd import OnReactionAdd
from discordbot.clienteventclasses.onready import OnReadyEvent
from discordbot.clienteventclasses.onstickercreate import OnStickerCreate
from discordbot.clienteventclasses.onthreadcreate import OnThreadCreate
from discordbot.clienteventclasses.onthreadupdate import OnThreadUpdate
from discordbot.clienteventclasses.onvoicestatechange import OnVoiceStateChange

# context commands
from discordbot.contextcommands.message_delete import ContextDeleteMessage
from discordbot.contextcommands.user_gift import ContextUserGift
from discordbot.embedmanager import EmbedManager

# modals
from discordbot.modals.betcreate import BetCreateModal
from discordbot.modals.reminder import ReminderModal
from discordbot.modals.suggest import SuggestModal

# slash commands
from discordbot.slashcommandeventclasses.active import Active
from discordbot.slashcommandeventclasses.admin_give import AdminGive
from discordbot.slashcommandeventclasses.autogenerate import AutoGenerate
from discordbot.slashcommandeventclasses.bless import Bless
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.config import Config
from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.slashcommandeventclasses.help import Help
from discordbot.slashcommandeventclasses.highscore import HighScore
from discordbot.slashcommandeventclasses.king_rename import KingRename
from discordbot.slashcommandeventclasses.leaderboard import Leaderboard
from discordbot.slashcommandeventclasses.pending import Pending
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.slashcommandeventclasses.pledge import Pledge
from discordbot.slashcommandeventclasses.predict import Predict
from discordbot.slashcommandeventclasses.refresh import RefreshBet
from discordbot.slashcommandeventclasses.stats import Stats
from discordbot.slashcommandeventclasses.taxrate import TaxRate
from discordbot.slashcommandeventclasses.transactions import TransactionHistory
from discordbot.slashcommandeventclasses.view import View
from discordbot.slashcommandeventclasses.wordle import Wordle

# task imports
from discordbot.tasks.activitychanger import ActivityChanger
from discordbot.tasks.annualawards import AnnualBSEddiesAwards
from discordbot.tasks.basetask import BaseTask
from discordbot.tasks.betcloser import BetCloser
from discordbot.tasks.betreminder import BetReminder
from discordbot.tasks.celebrations import Celebrations
from discordbot.tasks.dailyvallytask import AfterWorkVally
from discordbot.tasks.eddiegains import EddieGainMessager
from discordbot.tasks.eddiekingtask import BSEddiesKingTask
from discordbot.tasks.guildchecker import GuildChecker
from discordbot.tasks.messagesync import MessageSync
from discordbot.tasks.monthlyawards import MonthlyBSEddiesAwards
from discordbot.tasks.releasechecker import ReleaseChecker
from discordbot.tasks.reminders import RemindersTask
from discordbot.tasks.revolutiontask import BSEddiesRevolutionTask
from discordbot.tasks.taskmanager import TaskManager
from discordbot.tasks.threadmutetask import ThreadSpoilerTask
from discordbot.tasks.wordlereminder import WordleReminder
from discordbot.tasks.wordletask import WordleTask
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.points import UserPoints


class CommandManager:
    """Class for registering all the client events and slash commands.

    Needs to be initialised with a client and a list of guild IDS.

    Only the constructor needs to be called in this class for it to register everything.
    """

    def __init__(  # noqa: PLR0915
        self: "CommandManager",
        client: BSEBot,
        guilds: list,
        logger: logging.Logger,
        giphy_token: str | None = None,
        github_token: str | None = None,
    ) -> None:
        """Initialisation method.

        This does all the work in this class and no other methods need to be called.
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

        :param client: BSEBot object that represents our bot
        :param guilds: list of guild IDs that we're listening on
        :param logger:  logger object for logging
        :param debug_mode: whether we're in debug mode or not
        :param giphy_token:
        :param github_token:
        """
        self.client = client
        self.guilds = guilds
        self.logger = logger
        self.giphy_token = giphy_token
        self.github_token = github_token

        self.embeds = EmbedManager(self.logger)

        self.giphyapi = GiphyAPI(self.giphy_token)
        self.githubapi = GitHubAPI(self.github_token)

        # mongo interaction classes
        self.user_points = UserPoints()
        self.user_bets = UserBets(guilds)

        self.__get_cached_messages_list()

        # client event classes
        self.on_ready = OnReadyEvent(client, guilds, self.logger)
        self.on_reaction_add = OnReactionAdd(client, guilds, self.logger)
        self.on_message = OnMessage(client, guilds, self.logger)
        self.on_message_edit = OnMessageEdit(client, guilds, self.logger)
        self.on_member_join = OnMemberJoin(client, guilds, self.logger)
        self.on_member_leave = OnMemberLeave(client, guilds, self.logger)
        self.direct_message = OnDirectMessage(client, guilds, self.logger, self.giphyapi)
        self.on_thread_create = OnThreadCreate(client, guilds, self.logger)
        self.on_thread_update = OnThreadUpdate(client, guilds, self.logger)
        self.on_emoji_create = OnEmojiCreate(client, guilds, self.logger)
        self.on_sticker_create = OnStickerCreate(client, guilds, self.logger)
        self.on_voice_state_change = OnVoiceStateChange(client, guilds, self.logger)

        # slash command classes
        self.bseddies_active = Active(client, guilds, self.logger)
        self.bseddies_gift = Gift(client, guilds, self.logger)
        self.bseddies_view = View(client, guilds, self.logger)
        self.bseddies_leaderboard = Leaderboard(client, guilds, self.logger)
        self.bseddies_close = CloseBet(client, guilds, self.logger)
        self.bseddies_config = Config(client, guilds, self.logger)
        self.bseddies_place = PlaceBet(client, guilds, self.logger)
        self.bseddies_pending = Pending(client, guilds, self.logger)
        self.bseddies_transactions = TransactionHistory(client, guilds, self.logger)
        self.bseddies_admin_give = AdminGive(client, guilds, self.logger)
        self.bseddies_high_score = HighScore(client, guilds, self.logger)
        self.bseddies_predict = Predict(client, guilds, self.logger)
        self.bseddies_refresh = RefreshBet(client, guilds, self.logger)
        self.bseddies_autogenerate = AutoGenerate(client, guilds, self.logger)
        self.bseddies_tax_rate = TaxRate(client, guilds, self.logger)
        self.bseddies_stats = Stats(client, guilds, self.logger)
        self.bseddies_king_rename = KingRename(client, guilds, self.logger)
        self.bseddies_pledge = Pledge(client, guilds, self.logger)
        self.bseddies_bless = Bless(client, guilds, self.logger)
        self.bseddies_wordle = Wordle(client, guilds, self.logger)

        # dynamically gets all the defined application commands
        # from the class attributes
        all_commands = [
            attr[1]
            for attr in inspect.getmembers(self, lambda x: not inspect.isroutine(x))
            if isinstance(attr[1], BSEddies)
        ]

        self.bseddies_help = Help(client, guilds, self.logger, all_commands)

        # context commands
        self.message_delete = ContextDeleteMessage(client, guilds, self.logger)
        self.user_gift = ContextUserGift(client, guilds, self.logger, self.bseddies_gift)

        # tasks
        self.guild_checker_task = GuildChecker(
            self.client,
            guilds,
            self.logger,
            [],
            self.on_ready,
            self.githubapi,
            self.bseddies_place,
            self.bseddies_close,
        )

        startup_tasks = [
            self.guild_checker_task,
        ]

        self.bet_closer_task = BetCloser(
            self.client,
            guilds,
            self.logger,
            startup_tasks,
            self.bseddies_place,
            self.bseddies_close,
        )

        self.activity_changer = ActivityChanger(self.client, guilds, self.logger, startup_tasks)
        self.bet_reminder_task = BetReminder(self.client, guilds, self.logger, startup_tasks)
        self.eddie_gain_message_task = EddieGainMessager(self.client, guilds, self.logger, startup_tasks)
        self.eddie_king_task = BSEddiesKingTask(self.client, guilds, self.logger, startup_tasks)
        self.revolution_task = BSEddiesRevolutionTask(self.client, guilds, self.logger, startup_tasks, self.giphy_token)
        self.release_task = ReleaseChecker(self.client, guilds, self.logger, startup_tasks, self.githubapi)
        self.thread_task = ThreadSpoilerTask(self.client, guilds, self.logger, startup_tasks)
        self.message_sync = MessageSync(self.client, guilds, self.logger, startup_tasks, self.on_message)
        self.vally_task = AfterWorkVally(self.client, guilds, self.logger, startup_tasks)
        self.monthly_awards_task = MonthlyBSEddiesAwards(self.client, guilds, self.logger, startup_tasks)
        self.annual_awards_task = AnnualBSEddiesAwards(self.client, guilds, self.logger, startup_tasks)
        self.wordle_task = WordleTask(self.client, guilds, self.logger, startup_tasks)
        self.wordle_reminder = WordleReminder(self.client, guilds, self.logger, startup_tasks)
        self.celebrations_task = Celebrations(self.client, guilds, self.logger, startup_tasks)
        self.reminders_task = RemindersTask(self.client, guilds, self.logger, startup_tasks)

        # dynamically gets all the defined tasks
        # from the class attributes
        all_tasks = [
            attr[1]
            for attr in inspect.getmembers(self, lambda x: not inspect.isroutine(x))
            if isinstance(attr[1], BaseTask)
        ]

        self.task_manager = TaskManager(self.client, guilds, self.logger, startup_tasks, all_tasks)

        # call the methods that register the events we're listening for
        self._register_client_events()
        self._register_slash_commands()
        self._register_context_commands()

    # noinspection PyProtectedMember
    def __get_cached_messages_list(self: "CommandManager") -> list:
        """Method for getting a list of cached message IDs.

        Returns:
            list: list of cached messages.
        """
        deque = self.client.cached_messages._SequenceProxy__proxied  # noqa: SLF001
        return [d.id for d in deque]

    def _register_client_events(self: "CommandManager") -> None:  # noqa: PLR0915, C901
        """This method registers all the 'client events'.

        Client Events are normal discord events that we can listen to.
        A full list of events can be found here: https://docs.pycord.dev/en/stable/api.html#event-reference.

        Each event must be it's own async method with a @self.client.event decorator so that it's actually
        registered. None of these methods defined here will ever be called manually by anyone. The methods are called
        by the CLIENT object and that will pass in all the required parameters.

        Additionally, the method is called automatically from this class' constructor and shouldn't be called anywhere
        else.

        Returns:
            None
        """

        @self.client.event
        async def on_ready() -> None:
            """Event that handles when we're 'ready'."""
            await self.on_ready.on_ready()

        @self.client.event
        async def on_member_join(member: discord.Member) -> None:
            """Event that's called when a new member joins the guild.

            Args:
                member (discord.Member): the member that joins
            """
            self.on_member_join.on_join(member)

        @self.client.event
        async def on_member_remove(member: discord.Member) -> None:
            """Event that's called when a member leaves the guild.

            Args:
                member (discord.Member): the member that joins
            """
            self.on_member_leave.on_leave(member)

        @self.client.event
        async def on_raw_reaction_add(payload: discord.RawReactionActionEvent) -> None:
            """This event catches EVERY reaction event on every message in the server.

            However, any operations we want to perform are a bit slower as we need to 'fetch' the message
            before we have all the data we have. BUT, we need to handle reactions to all messages as a user may
            react to an older message that isn't in the cache and we can't just not do anything.

            If the message is in the cache - then this event will fire and so will on_reaction_add. To prevent that,
            and to keep on_reaction_add for cached messages and be faster, we check if the message_id is already
            in the cache. If it is, then we can safely ignore it here. Otherwise we need to handle it.

            Args:
                payload (discord.RawReactionActionEvent): the raw payload
            """
            cached_messages = self.__get_cached_messages_list()
            if payload.message_id in cached_messages:
                # message id is already in the cache
                return

            guild = await self.client.fetch_guild(payload.guild_id)  # type: discord.Guild
            user = await self.client.fetch_user(payload.user_id)  # type: discord.User

            if user.bot:
                return

            channel = await self.client.fetch_channel(payload.channel_id)  # type: discord.TextChannel
            partial_message = channel.get_partial_message(payload.message_id)  # type: discord.PartialMessage
            message = await partial_message.fetch()  # type: discord.Message

            await self.on_reaction_add.handle_reaction_event(message, guild, channel, payload.emoji.name, user)

        @self.client.event
        async def on_reaction_add(reaction: discord.Reaction, user: discord.User) -> None:
            """This event is triggered when anyone 'reacts' to a message in a guild that the bot is in.

            Will even be triggered by it's own reactions. However, this only triggers for messages that the bot
            has in it's cache - reactions to older messages will only trigger a 'on_raw_reaction_add' event.

            Here, we simply hand it off to another class to deal with.

            Args:
                reaction (discord.Reaction): the reaction object
                user (discord.User): the user that triggered the reaction
            """
            await self.on_reaction_add.handle_reaction_event(
                reaction.message,
                reaction.message.guild,
                reaction.message.channel,
                reaction.emoji,
                user,
            )

        @self.client.event
        async def on_thread_create(thread: discord.Thread) -> None:
            """Event handler for on_thread_create.

            Args:
                thread (discord.Thread): the created Thread
            """
            await self.on_thread_create.on_thread_create(thread)

        @self.client.event
        async def on_thread_update(before: discord.Thread, after: discord.Thread) -> None:
            """Event handler for on_thread_update.

            Args:
                before (discord.Thread): the Thread before
                after (discord.Thread): the Thread after
            """
            await self.on_thread_update.on_update(before, after)

        @self.client.event
        async def on_raw_thread_update(payload: discord.RawThreadUpdateEvent) -> None:
            """Handler for on_raw_thread_update.

            Args:
                payload (discord.RawThreadUpdateEvent): the raw payload
            """
            if payload.thread:
                # already in internal cache - so on_thread_update can handle that
                return

            thread = await self.client.fetch_channel(payload.thread_id)  # type: discord.Thread
            await self.on_thread_update.on_update(thread, thread)

        @self.client.event
        async def on_message(message: discord.Message) -> None:
            """Handler for on_message event.

            This is the 'message' event. Whenever a message is sent in a guild that the bot is listening for -
            we will enact this code. Here, we simply hand it off to another class to deal with.

            Args:
                message (discord.Message): the message object
            """
            if message.flags.ephemeral:
                # message is ephemeral - do nothing with it
                return

            if (
                message.author.id != self.client.user.id
                and type(message.channel) is discord.channel.DMChannel
                and message.type != discord.MessageType.application_command
            ):
                # this means we've received a Direct message!
                # we'll have to handle this differently
                self.logger.debug("%s - %s", message, message.content)
                await self.direct_message.dm_received(message)
                return

            if type(message.channel) is discord.channel.DMChannel and message.author.id == self.client.user.id:
                # message in DM channel from ourselves
                return

            await self.on_message.message_received(message)

        @self.client.event
        async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent) -> None:
            """Raw event for message edit events.

            Args:
                payload (discord.RawMessageUpdateEvent): the payload
            """
            cached_messages = self.__get_cached_messages_list()
            if payload.message_id in cached_messages:
                # message id is already in the cache
                return

            channel = await self.client.fetch_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await self.on_message_edit.message_edit(None, message)

        @self.client.event
        async def on_message_edit(before: discord.Message, after: discord.Message) -> None:
            """Listens to the on_message_edit event.

            Args:
                before (discord.Message): the message _before_
                after (discord.Message): _the message _after_
            """
            await self.on_message_edit.message_edit(before, after)

        @self.client.event
        async def on_guild_emojis_update(
            guild: discord.Guild,
            before: discord.Sequence[discord.Emoji],
            after: discord.Sequence[discord.Emoji],
        ) -> None:
            """For updating our internal list of emojis.

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
            after: discord.Sequence[discord.Sticker],
        ) -> None:
            """For updating our internal list of emojis.

            Args:
                guild (discord.Guild): the Guild object
                before (discord.Sequence[discord.Emoji]): list of stickers before
                after (discord.Sequence[discord.Emoji]): list of stickers after
            """
            await self.on_sticker_create.on_stickers_update(guild.id, before, after)

        @self.client.event
        async def on_voice_state_update(
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState,
        ) -> None:
            """Logging time in VC.

            Args:
                member (discord.Member): the Member object
                before (discord.VoiceState): Voice state before
                after (discord.VoiceState): Voice state after
            """
            await self.on_voice_state_change.on_voice_state_change(member, before, after)

    def _register_slash_commands(self: "CommandManager") -> None:  # noqa: C901, PLR0915
        """This method registers all the 'slash commands'.

        Slash Commands are commands users can use in discord.
        Each command must be it's own async method with a relevant decorator so that it's actually
        registered. None of these methods defined here will ever be called manually by anyone. The methods are called
        by the CLIENT object and that will pass in all the required parameters.

        Additionally, the method is called automatically from this class' constructor and shouldn't be called anywhere
        else.
        """

        @self.client.command(description="View your total BSEddies")
        async def view(ctx: discord.ApplicationContext) -> None:
            """Slash command that allows the user to see how many BSEddies they have.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_view.view(ctx)

        @self.client.command(description="View the current BSEddies leaderboard")
        async def leaderboard(ctx: discord.ApplicationContext) -> None:
            """Slash command that allows the user to see the BSEddies leaderboard.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_leaderboard.leaderboard(ctx)

        @self.client.command(description="See your estimated salary gain for today so far")
        async def predict(ctx: discord.ApplicationContext) -> None:
            """Slash command that allows the user to see their predict daily salary.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_predict.predict(ctx)

        @self.client.command(description="View the BSEddies High Scores.")
        async def highscores(ctx: discord.ApplicationContext) -> None:
            """Slash command that allows the user to see the BSEddies high scores.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_high_score.highscore(ctx)

        @self.client.command(description="View all the active bets in the server.")
        async def active(ctx: discord.ApplicationContext) -> None:
            """Slash commands lists all the active bets in the system.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_active.active(ctx)

        @self.client.command(description="View all the unresolved bets you have betted on.")
        async def pending(ctx: discord.ApplicationContext) -> None:
            """Slash commands lists all the pending bets in the system for the user.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_pending.pending(ctx)

        @self.client.command(description="Gift some of your eddies to a friend")
        async def gift(
            ctx: discord.ApplicationContext,
            friend: discord.Option(discord.User),
            amount: discord.Option(int),
        ) -> None:
            """A slash command that allows users to gift eddies to their friends.

            It was two main arguments:
                - FRIEND: The user in the server to gift BSEddies to
                - AMOUNT: The amount of BSEddies to gift

            Args:
                ctx (discord.ApplicationContext): the command context
                friend (discord.User): the user to gift eddies to
                amount (int): the amount of eddies to gift
            """
            await self.bseddies_gift.gift_eddies(ctx, friend, amount)

        @self.client.command(description="View your transaction history.")
        async def transactions(
            ctx: discord.ApplicationContext,
            full: discord.Option(
                bool,
                description="Do you want the full transaction history?",
                default=False,
            ),
        ) -> None:
            """Slash command that allows the user to see their eddie transaction history.

            Args:
                ctx (discord.ApplicationContext): the command context
                full (bool): whether to do the full transaction history or not
            """
            await ctx.defer(ephemeral=True)
            await self.bseddies_transactions.transaction_history(ctx, full)

        @self.client.command(description="Create a bet")
        async def create(ctx: discord.ApplicationContext) -> None:
            """Command to create a bet.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            modal = BetCreateModal(client=self.client, guilds=self.guilds, logger=self.logger, title="Create a bet")
            await ctx.response.send_modal(modal)

        @self.client.command(description="Autogenerate bets")
        async def autogenerate(ctx: discord.ApplicationContext) -> None:
            """Command to autogenerate some bets.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await ctx.defer(ephemeral=True)
            await self.bseddies_autogenerate.create_auto_generate_view(ctx)

        @self.client.command(description="Place a bet")
        async def place(ctx: discord.ApplicationContext) -> None:
            """This is the command that allows users to place BSEddies.  on currently active bets.

            Users can only bet on "active" bets. IE ones that haven't timed out or ones that have results already.
            Users can't bet on a different result to one that they've already bet on.
            Users can't bet a negative amount of BSEddies.
            Users can't bet on a result that doesn't exist for that bet.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_place.create_bet_view(ctx)

        @self.client.command(description="Close a bet by providing a result and award those SWEET EDDIES.")
        async def close(ctx: discord.ApplicationContext) -> None:
            """This is the command that closes a bet.

            Closing a bet requires a result emoji. Once a bet is "closed";
            no-one can bet on it and the winners will gain their BSEddies.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_close.create_bet_view(ctx)

        @self.client.command(
            description="Give a user some eddies",
        )
        async def admin_give(ctx: discord.ApplicationContext, user: discord.User, amount: int) -> None:
            """Slash command for an admin to give eddies for someone.

            Args:
                ctx (discord.ApplicationContext): the command context
                user (discord.User): the user to give eddies to
                amount (int): the eddies to give them
            """
            await self.bseddies_admin_give.admin_give(ctx, user, amount)

        @self.client.command(description="Set server eddies tax rate")
        async def taxrate(ctx: discord.ApplicationContext) -> None:
            """Slash command to set tax rate.

            Args:
                ctx (discord.ApplicationContext): _description_
            """
            await self.bseddies_tax_rate.create_tax_view(ctx)

        @self.client.command(description="Pay to rename one of the BSEddies roles")
        async def rename(
            ctx: discord.ApplicationContext,
            name: str,
            role: discord.Option(str, choices=["king", "supporter", "revolutionary"]),
        ) -> None:
            """Slash command to rename the BSEddies roles.

            Args:
                ctx (discord.ApplicationContext): the command context
                name (str): the new name of the role
                role (str): the role to be renamed
            """
            await self.bseddies_king_rename.rename(ctx, name, role)

        @self.client.command(description="Refresh a bet from the DB")
        async def refresh(ctx: discord.ApplicationContext) -> None:
            """Slash command to refresh a bet.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_refresh.create_refresh_view(ctx, None)

        @self.client.command(description="Pledge your support to the KING")
        async def pledge(ctx: discord.ApplicationContext) -> None:
            """Command to pledge to a side.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_pledge.create_pledge_view(ctx)

        @self.client.command(description="Bless your supporters or the server")
        async def bless(ctx: discord.ApplicationContext) -> None:
            """Command to bless.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_bless.create_bless_view(ctx)

        @self.client.command(description="Configure BSEBot")
        async def config(ctx: discord.ApplicationContext) -> None:
            """Command to configure the bot.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_config.root_config(ctx)

        @self.client.command(description="Help")
        async def help(ctx: discord.ApplicationContext) -> None:  # noqa: A001
            """Help command.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_help.help(ctx)

        @self.client.command(description="Suggest an improvement")
        async def suggest(ctx: discord.ApplicationContext) -> None:
            """Command for suggesting improvements.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            modal = SuggestModal(logger=self.logger, github_api=self.githubapi, title="Suggest an improvement")
            await ctx.response.send_modal(modal)

        @self.client.command(description="Set a reminder")
        async def remindme(ctx: discord.ApplicationContext) -> None:
            """Command for reminders.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            modal = ReminderModal(self.logger, None, title="Set a reminder")
            await ctx.response.send_modal(modal)

        @self.client.command(description="See some stats")
        async def stats(ctx: discord.ApplicationContext) -> None:
            """Stats Slash command.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_stats.create_stats_view(ctx)

        @self.client.command(description="See some Wordle stats")
        async def wordle(ctx: discord.ApplicationContext) -> None:
            """Command for wordle stats.

            Args:
                ctx (discord.ApplicationContext): the command context
            """
            await self.bseddies_wordle.wordle(ctx)

    def _register_context_commands(self: "CommandManager") -> None:
        """Registers our context menu commands."""

        @self.client.message_command(name="Pin message")
        async def pin_message(ctx: discord.ApplicationContext, message: discord.Message) -> None:
            """Allows users to pin a message.

            Args:
                ctx (discord.ApplicationContext): the command context
                message (discord.Message): the message to pin
            """
            with contextlib.suppress(discord.HTTPException):
                await message.pin(reason=f"{ctx.author.name} has pinned this message")
            await ctx.respond(content="Pinned", ephemeral=True, delete_after=5)

        @self.client.message_command(name="Delete message")
        async def delete_message(ctx: discord.ApplicationCommand, message: discord.Message) -> None:
            """Allows BSEddies admins to delete a message.

            Args:
                ctx (discord.ApplicationCommand): the command context
                message (discord.Message): the message to delete
            """
            await self.message_delete.message_delete(ctx, message)

        @self.client.message_command(name="Remind me")
        async def remind_me(ctx: discord.ApplicationCommand, message: discord.Message) -> None:
            """Allows triggering of the reminder modal using an existing message.

            Args:
                ctx (discord.ApplicationCommand): the command context
                message (discord.Message): the message to trigger a reminder
            """
            modal = ReminderModal(self.logger, message.id, title="Set a reminder")
            await ctx.response.send_modal(modal)

        @self.client.user_command(name="Gift")
        async def gift(ctx: discord.ApplicationCommand, user: discord.Member) -> None:
            """_summary_.

            Args:
                ctx (discord.ApplicationCommand): the command context
                user (discord.Member): the user to gift eddies to
            """
            await self.user_gift.user_gift(ctx, user)
