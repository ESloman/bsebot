"""Task for Guild Chcker."""

import datetime
from logging import Logger

import discord
from discord.ext import tasks

from apis.github import GitHubAPI
from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.onready import OnReadyEvent
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.tasks.basetask import BaseTask
from discordbot.views.bet import BetView
from discordbot.views.leaderboard import LeaderBoardView
from discordbot.views.revolution import RevolutionView


class GuildChecker(BaseTask):
    """Class for guild checker task."""

    def __init__(  # noqa: PLR0913, PLR0917
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        on_ready: OnReadyEvent,
        github_api: GitHubAPI,
        place: PlaceBet,
        close: CloseBet,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.guild_checker

        self.on_ready = on_ready
        self.embed_manager = EmbedManager(logger)
        self.github = github_api

        self.close = close
        self.place = place

        self.task.start()

    @tasks.loop(hours=12)
    async def guild_checker(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """Loop that makes sure that guild information is synced correctly."""
        datetime.datetime.now()

        self.logger.info("Running guild sync")
        async for guild in self.bot.fetch_guilds():
            self.logger.debug("Checking guild: %s - %s", guild.id, guild.name)

            db_guild = self.guilds.get_guild(guild.id)
            if not db_guild:
                # gotta insert into database
                self.guilds.insert_guild(
                    guild.id,
                    guild.name,
                    guild.owner_id,
                    guild.created_at,
                )
                # get new instance of db_guild
                db_guild = self.guilds.get_guild(guild.id)
                self.guilds.update_tax_history(guild.id, 0.1, 0.0, self.bot.user.id)

            self.logger.debug("Checking guild salary minimum")
            if db_guild.daily_minimum is None:
                self.guilds.set_daily_minimum(guild.id, 4)

            if db_guild.name != guild.name:
                self.logger.debug("Updating db name for %s", guild.name)
                self.guilds.update({"_id": db_guild._id}, {"$set": {"name": guild.name}})  # noqa: SLF001

            self.logger.debug("Checking guilds for new members")
            members = await guild.fetch_members().flatten()
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
            if member_ids:
                # actually managed to get members
                _users = self.user_points.get_all_users_for_guild(guild.id)
                _users = [u for u in _users if not u.inactive]
                for user in _users:
                    if user["uid"] not in member_ids:
                        self.user_points.update({"_id": user._id}, {"$set": {"inactive": True}})  # noqa: SLF001
                        self.activities.add_activity(user._id, guild.id, ActivityTypes.SERVER_LEAVE)  # noqa: SLF001

            self.logger.info("Checking guild emojis")
            # sort out emojis
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

            self.logger.info("Checking guild stickers")
            # sort out stickers
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

            # thread stuff
            # join all threads
            self.logger.debug("Joining threads")
            channels = await guild.fetch_channels()
            for channel in channels:
                if type(channel) != discord.channel.TextChannel:
                    continue

                if not channel.threads:
                    continue

                for thread in channel.threads:
                    if thread.archived or thread.locked:
                        continue

                    thread_members = await thread.fetch_members()
                    if self.bot.user.id not in [member.id for member in thread_members]:
                        await thread.join()
                        self.logger.debug("Joined %s", thread.name)

                    thread_info = self.spoilers.get_thread_by_id(guild.id, thread.id)

                    if not thread_info:
                        self.logger.debug("No info for thread %s, %s. Inserting now.", thread.id, thread.name)
                        self.spoilers.insert_spoiler_thread(
                            guild.id,
                            thread.id,
                            thread.name,
                            thread.created_at,
                            thread.owner_id,
                        )

            # sync threads in db with actual threads
            threads = self.spoilers.get_all_threads(guild.id)
            for thread_info in threads:
                if not thread_info.created or not thread_info.owner:
                    try:
                        thread = await guild.fetch_channel(thread_info.thread_id)
                    except discord.Forbidden:
                        continue

                    self.spoilers.update(
                        {"_id": thread_info._id},  # noqa: SLF001
                        {"$set": {"created_at": thread.created_at, "owner": thread.owner.id}},
                    )

            if self.finished:
                self.logger.info("Finished checking %s", guild.name)
                continue

            # only care about the stuff below on first run
            # theoretically event views should be initialised now
            # same for all the open bet views

            self.logger.debug("Initialising event views")
            if events := self.revolutions.get_open_events(guild.id):
                if len(events) > 1:
                    self.logger.debug("???")
                    continue
                event = events[0]
                view = RevolutionView(self.bot, event, self.logger)
                view.toggle_stuff(False)
                self.bot.add_view(view)
                message_id = event["message_id"]
                channel_id = event["channel_id"]

                channel = await self.bot.fetch_channel(channel_id)
                message = channel.get_partial_message(message_id)

            # find all open bets
            self.logger.info("Initialising bet views")
            bets = self.user_bets.get_all_active_bets(guild.id)
            other_bets = self.user_bets.get_all_inactive_pending_bets(guild.id)
            bets.extend(other_bets)
            for bet in bets:
                message_id = bet["message_id"]
                channel_id = bet["channel_id"]
                if not channel_id or not message_id:
                    continue

                try:
                    channel = await self.bot.fetch_channel(channel_id)
                except discord.errors.NotFound:
                    # possible the channel no longer exists
                    self.logger.debug("Issue with fetching channel: %s, %s", channel_id, bet)
                    continue

                message = channel.get_partial_message(message_id)

                embed = self.embed_manager.get_bet_embed(guild, bet)
                view = BetView(bet, self.place, self.close)
                content = f"# {bet['title']}\n_Created by <@{bet['user']}>_"
                try:
                    await message.edit(content=content, view=view, embed=embed)
                except (discord.NotFound, discord.Forbidden):
                    continue

            self.bot.add_view(LeaderBoardView(self.embed_manager))

            self.logger.info("Finishing checking %s", guild.name)

        self.finished = True

    @guild_checker.before_loop
    async def before_guild_checker(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
