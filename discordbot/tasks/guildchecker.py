"""Task for Guild Chcker."""

import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from discordbot.views.bet import BetView
from discordbot.views.leaderboard import LeaderBoardView
from discordbot.views.revolution import RevolutionView
from mongo.datatypes.guild import GuildDB

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.close import CloseBet
    from discordbot.slashcommandeventclasses.place import PlaceBet


class GuildChecker(BaseTask):
    """Class for guild checker task."""

    def __init__(
        self,
        bot: BSEBot,
        startup_tasks: list[BaseTask],
        place: "PlaceBet",
        close: "CloseBet",
        start: bool = False,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks.
            place (PlaceBet): the PlaceBet class
            close (CloseBet): the CloseBet class
            start (bool): whether to start the task. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule(range(7), [3], 15)
        self.task = self.guild_checker
        self.finished: bool = False

        self.embed_manager = EmbedManager()

        self.close: CloseBet = close
        self.place: PlaceBet = place

        # override to run at startup
        self.schedule.overriden = not self.finished

        if start:
            self.task.start()

    def _create_new_guild(self, guild: discord.Guild) -> GuildDB:
        """Inserting a new guild into the database.

        Args:
            guild (discord.Guild): the guild to insert

        Returns:
            GuildDB: the created guild object
        """
        db_guild = self.guilds.insert_guild(
            guild.id,
            guild.name,
            guild.owner_id,
            guild.created_at,
        )
        # get new instance of db_guild
        self.guilds.update_tax_history(guild.id, 0.1, 0.0, self.bot.user.id)
        return db_guild

    def _check_guild_basic_info(self, guild: discord.Guild) -> GuildDB:
        """Checks a guild's basic information.

        Given a guild, check some basic information that should be present
        in the database. Returns the GuildDB object.

        Args:
            guild (discord.Guild): the guild to check

        Returns:
            GuildDB: the guild DB object
        """
        db_guild = self.guilds.get_guild(guild.id)
        if not db_guild:
            db_guild = self._create_new_guild(guild)

        self.logger.debug("Checking guild salary minimum")
        if db_guild.daily_minimum is None:
            self.guilds.set_daily_minimum(guild.id, 4)

        if db_guild.name != guild.name:
            self.logger.debug("Updating db name for %s", guild.name)
            self.guilds.update({"_id": db_guild._id}, {"$set": {"name": guild.name}})  # noqa: SLF001
        return db_guild

    async def _check_guild_members(self, guild: discord.Guild) -> None:
        """Checks a guild's members match what we have in the database.

        Args:
            guild (discord.Guild): the guild to check
        """
        members = await guild.fetch_members().flatten()

        self.logger.debug("Checking guilds for new members")
        for member in members:  # type: discord.Member
            if member.bot:
                continue

            self.logger.debug("Checking %s - %s", member.id, member.name)
            name = member.nick or member.name
            user = self.user_points.find_user(member.id, guild.id)
            if not user:
                self.user_points.create_user(member.id, guild.id, name, False)
                self.activities.add_activity(member.id, guild.id, ActivityTypes.SERVER_JOIN)
                self.logger.debug(
                    "Creating new user entry for %s - %s for %s - %s", member.id, member.name, guild.id, guild.name
                )
                continue

            if name != user.name:
                self.logger.debug("Updating db name for %s", name)
                self.user_points.update({"_id": user._id}, {"$set": {"name": name}})  # noqa: SLF001

        self.logger.debug("Checking for users that have left")
        member_ids = [member.id for member in members]
        if not member_ids:
            # exit here if we failed to get members (and therefore IDs)
            # otherwise we think everyone has left the server (which is not accurate)
            return
        _users = self.user_points.get_all_users_for_guild(guild.id)
        _users = [u for u in _users if not u.inactive]
        for user in _users:
            if user.uid not in member_ids:
                self.user_points.update({"_id": user._id}, {"$set": {"inactive": True}})  # noqa: SLF001
                self.activities.add_activity(user._id, guild.id, ActivityTypes.SERVER_LEAVE)  # noqa: SLF001

    async def _check_guild_emojis(self, guild: discord.Guild) -> None:
        """Checks we have all the guild emojis in the database.

        Args:
            guild (discord.Guild): the guild to check.
        """
        for emoji in guild.emojis:
            emoji_obj = await guild.fetch_emoji(emoji.id)
            emoji_db_obj = self.server_emojis.get_emoji(guild.id, emoji_obj.id)
            if not emoji_db_obj:
                self.logger.debug("%s doesn't exist in the DB yet - inserting", emoji_obj.name)
                self.server_emojis.insert_emoji(
                    emoji_obj.id,
                    emoji_obj.name,
                    emoji_obj.created_at,
                    emoji_obj.user.id,
                    guild.id,
                )

    async def _check_guild_stickers(self, guild: discord.Guild) -> None:
        """Checks we have all the guild stickers in the database.

        Args:
            guild (discord.Guild): the guild to check
        """
        for sticker in guild.stickers:
            stick_obj = await guild.fetch_sticker(sticker.id)
            sticker_db_obj = self.server_stickers.get_sticker(guild.id, stick_obj.id)
            if not sticker_db_obj:
                self.logger.info("%s doesn't exist in the DB yet - inserting", stick_obj.name)
                self.server_stickers.insert_sticker(
                    stick_obj.id,
                    stick_obj.name,
                    stick_obj.created_at,
                    stick_obj.user.id,
                    guild.id,
                )

    async def _join_threads_for_channel(self, guild: discord.Guild, channel: discord.channel.TextChannel) -> None:
        """Joins all the threads for a given channel.

        Args:
            guild (discord.Guild): the guild
            channel (discord.channel.TextChannel): the channel
        """
        for thread in channel.threads:
            if thread.archived or thread.locked:
                continue

            thread_members = await thread.fetch_members()
            if self.bot.user.id not in [member.id for member in thread_members]:
                await thread.join()
                self.logger.debug("Joined %s", thread.name)

            if self.spoilers.get_thread_by_id(guild.id, thread.id):
                continue

            self.logger.debug("No info for thread %s, %s. Inserting now.", thread.id, thread.name)
            self.spoilers.insert_spoiler_thread(
                guild.id,
                thread.id,
                thread.name,
                thread.created_at,
                thread.owner_id,
            )

    async def _check_guild_join_threads(self, guild: discord.Guild) -> None:
        """Joins all the threads to ensure we're in them.

        Args:
            guild (discord.Guild): the guild to check
        """
        channels = await guild.fetch_channels()
        for channel in channels:
            if channel.type not in {discord.ChannelType.text, discord.ChannelType.private}:
                continue

            if not channel.threads:
                continue

            await self._join_threads_for_channel(guild, channel)

    async def _check_threads(self, guild: discord.Guild) -> None:
        """Checks that our thread information is accurate.

        Args:
            guild (discord.Guild): the guild to check
        """
        threads = self.spoilers.get_all_threads(guild.id)
        for thread_info in threads:
            if thread_info.created and thread_info.owner:
                continue

            try:
                thread = await guild.fetch_channel(thread_info.thread_id)
            except discord.Forbidden:
                continue

            self.spoilers.update(
                {"_id": thread_info._id},  # noqa: SLF001
                {"$set": {"created_at": thread.created_at, "owner": thread.owner.id}},
            )

    def _check_events(self, guild: discord.Guild) -> None:
        """Checks open events and registers the views.

        Args:
            guild (discord.Guild): the guild to check events for
        """
        events = self.revolutions.get_open_events(guild.id)
        if not events:
            return
        if len(events) > 1:
            self.logger.debug("???")
            return
        event = events[0]
        view = RevolutionView(self.bot, event)
        view.toggle_stuff(False)
        self.bot.add_view(view)

    async def _check_bets(self, guild: discord.Guild) -> None:
        """Checks for open bets and makes sure to initialise their views.

        Args:
            guild (discord.Guild): the guild to check
        """
        bets = self.user_bets.get_all_active_bets(guild.id)
        other_bets = self.user_bets.get_all_inactive_pending_bets(guild.id)
        bets.extend(other_bets)
        for bet in bets:
            message_id = bet.message_id
            channel_id = bet.channel_id
            if not channel_id or not message_id:
                continue

            try:
                channel = await self.bot.fetch_channel(channel_id)
            except discord.errors.NotFound:
                # possible the channel no longer exists
                self.logger.debug("Issue with fetching channel: %s, %s", channel_id, bet)
                continue

            message = channel.get_partial_message(message_id)
            embed = self.embed_manager.get_bet_embed(bet)
            view = BetView(bet, self.place, self.close)
            content = f"# {bet.title}\n_Created by <@{bet.user}>_"
            try:
                await message.edit(content=content, view=view, embed=embed)
            except (discord.NotFound, discord.Forbidden):
                continue

    async def _check_channels(self, guild: discord.Guild) -> None:
        """Checks and caches our channels in the database.

        Args:
            guild (discord.Guild): the discord Guild to check.
        """
        channels = await guild.fetch_channels()
        for channel in channels:
            if channel.type == discord.ChannelType.category:
                # don't care about caching these
                continue
            # get channel here from database
            # if not in database - add it to the database
            # update information if incorrect
            channel_db = self.guild_channels.find_channel(guild.id, channel.id)
            if not channel_db:
                channel_db = self.guild_channels.insert_channel(
                    guild.id,
                    channel.id,
                    channel.type,
                    channel.name,
                    channel.created_at,
                    channel.category_id,
                    channel.is_nsfw(),
                )
                self.logger.debug("Inserted channel %s: %s into the database", channel_db.channel_id, channel_db.name)
                continue
            if channel_db.name != channel.name or channel_db.is_nsfw != channel.is_nsfw():
                self.guild_channels.update_channel(channel_db, channel.name, channel.is_nsfw())

    @tasks.loop(count=1)
    async def guild_checker(self) -> None:
        """Loop that makes sure that guild information is synced correctly."""
        datetime.datetime.now(tz=ZoneInfo("UTC"))

        self.logger.info("Running guild sync")
        async for guild in self.bot.fetch_guilds():
            self.logger.debug("Checking guild: %s - %s", guild.id, guild.name)

            self.user_bets.create_counter_document(guild.id)

            _: GuildDB = self._check_guild_basic_info(guild)

            self.logger.debug("Checking guild membership")
            await self._check_guild_members(guild)

            self.logger.info("Checking guild emojis")
            await self._check_guild_emojis(guild)

            self.logger.info("Checking guild stickers")
            await self._check_guild_stickers(guild)

            # thread stuff
            # join all threads
            self.logger.debug("Joining threads")
            await self._check_guild_join_threads(guild)

            # sync channel cache
            await self._check_channels(guild)

            # sync threads in db with actual threads
            await self._check_threads(guild)

            if self.finished:
                self.logger.info("Finished checking %s", guild.name)
                continue

            # only care about the stuff below on first run
            # theoretically event views should be initialised now
            # same for all the open bet views

            self.logger.debug("Initialising event views")
            self._check_events(guild)

            # find all open bets
            self.logger.info("Initialising bet views")
            await self._check_bets(guild)

            self.bot.add_view(LeaderBoardView(self.embed_manager))

            self.logger.info("Finishing checking %s", guild.name)

        self.finished = True
        self.schedule.overriden = False

    @guild_checker.before_loop
    async def before_guild_checker(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
