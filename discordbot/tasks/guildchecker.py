
import asyncio
import datetime
import os
import subprocess
from typing import Optional

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import TransactionTypes, ActivityTypes
from discordbot.clienteventclasses import OnReadyEvent
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses import BSEddiesPlaceBet, BSEddiesCloseBet
from discordbot.views import LeaderBoardView, RevolutionView, BetView

from mongo.bsedataclasses import CommitHash, SpoilerThreads
from mongo.bseticketedevents import RevolutionEvent
from mongo.bsepoints import Guilds, UserInteractions, ServerEmojis, ServerStickers, UserBets, UserPoints


class GuildChecker(commands.Cog):
    def __init__(self, bot: discord.Client, logger, on_ready: OnReadyEvent):
        self.bot = bot
        self.logger = logger
        self.finished = False
        self.on_ready = on_ready

        self.user_interactions = UserInteractions()
        self.events = RevolutionEvent()
        self.server_emojis = ServerEmojis()
        self.server_stickers = ServerStickers()
        self.guilds = Guilds()
        self.spoilers = SpoilerThreads()
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.embed_manager = EmbedManager(logger)
        self.hashes = CommitHash()

        guild_ids = [g.id for g in self.bot.guilds]
        self.close = BSEddiesCloseBet(bot, guild_ids, self.logger)
        self.place = BSEddiesPlaceBet(bot, guild_ids, self.logger)

        self.guild_checker.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.guild_checker.cancel()

    @tasks.loop(hours=12)
    async def guild_checker(self):
        """
        Loop that makes sure that guild information is synced correctly
        :return:
        """
        now = datetime.datetime.now()

        self.logger.info("Running guild sync")
        async for guild in self.bot.fetch_guilds():
            self.logger.info(f"Checking guild: {guild.id} - {guild.name}")

            db_guild = self.guilds.get_guild(guild.id)
            if not db_guild:
                # gotta insert into database
                db_guild = self.guilds.insert_guild(
                    guild.id,
                    guild.name,
                    guild.owner_id,
                    guild.created_at
                )

            self.logger.info("Checking guilds for new members")
            members = await guild.fetch_members().flatten()
            for member in members:  # type: discord.Member
                if member.bot:
                    continue

                self.logger.info(f"Checking {member.id} - {member.name}")
                user = self.user_points.find_user(member.id, guild.id)
                if not user:
                    self.user_points.create_user(member.id, guild.id, False)
                    self.logger.info(
                        f"Creating new user entry for {member.id} - {member.name} for {guild.id} - {guild.name}"
                    )

                    self.user_points.append_to_transaction_history(
                        member.id,
                        guild.id,
                        {
                            "type": TransactionTypes.USER_CREATE,
                            "amount": 10,
                            "timestamp": now,
                            "comment": "User created",
                        }
                    )
                    continue

            self.logger.info("Checking for users that have left")
            member_ids = [member.id for member in members]
            if member_ids:
                # actually managed to get members
                _users = self.user_points.get_all_users_for_guild(guild.id)
                _users = [u for u in _users if not u.get("inactive")]
                for user in _users:
                    if user["uid"] not in member_ids:

                        self.user_points.update({"_id": user["_id"]}, {"$set": {"inactive": True}})
                        self.user_points.append_to_activity_history(
                            user["uid"],
                            guild.id,
                            {
                                "type": ActivityTypes.SERVER_LEAVE,
                                "timestamp": now
                            }
                        )

            self.logger.info("Checking guild emojis")
            # sort out emojis
            for emoji in guild.emojis:
                emoji_obj = await guild.fetch_emoji(emoji.id)
                emoji_db_obj = self.server_emojis.get_emoji(guild.id, emoji_obj.id)
                if not emoji_db_obj:
                    self.logger.info(f"{emoji_obj.name} doesn't exist in the DB yet - inserting")
                    self.server_emojis.insert_emoji(
                        emoji_obj.id,
                        emoji_obj.name,
                        emoji_obj.created_at,
                        emoji_obj.user.id,
                        guild.id
                    )

            self.logger.info("Checking guild stickers")
            # sort out stickers
            for sticker in guild.stickers:
                stick_obj = await guild.fetch_sticker(sticker.id)
                sticker_db_obj = self.server_stickers.get_sticker(guild.id, stick_obj.id)
                if not sticker_db_obj:
                    self.logger.info(f"{stick_obj.name} doesn't exist in the DB yet - inserting")
                    self.server_stickers.insert_sticker(
                        stick_obj.id,
                        stick_obj.name,
                        stick_obj.created_at,
                        stick_obj.user.id,
                        guild.id
                    )

            # thread stuff
            # join all threads
            self.logger.info("Joining threads")
            channels = await guild.fetch_channels()
            for channel in channels:
                if type(channel) not in [discord.channel.TextChannel]:
                    continue

                if not channel.threads:
                    continue

                for thread in channel.threads:
                    if thread.archived or thread.locked:
                        continue

                    thread_members = await thread.fetch_members()
                    if self.bot.user.id not in [member.id for member in thread_members]:
                        await thread.join()
                        self.logger.info(f"Joined {thread.name}")

                    thread_info = self.spoilers.get_thread_by_id(BSE_SERVER_ID, thread.id)

                    if not thread_info:
                        self.logger.info(f"No info for thread {thread.id}, {thread.name}. Inserting now.")
                        self.spoilers.insert_spoiler_thread(
                            guild.id,
                            thread.id,
                            thread.name,
                            thread.created_at,
                            thread.owner_id
                        )

            if self.finished:
                self.logger.info(f"Finished checking {guild.name}")
                continue

            # only care about the stuff below on first run
            # theoretically event views should be initialised now
            # same for all the open bet views
            # don't need to do the update log either

            self.logger.info("Initialising event views")
            if events := self.events.get_open_events(guild.id):
                if len(events) > 1:
                    self.logger.info("???")
                    continue
                event = events[0]
                view = RevolutionView(self.bot, event, self.logger)
                view.toggle_stuff(False)
                self.bot.add_view(view)
                message_id = event["message_id"]
                channel_id = event["channel_id"]

                channel = await guild.fetch_channel(channel_id)
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
                    channel = await guild.fetch_channel(channel_id)
                except discord.errors.NotFound:
                    # possible the channel no longer exists
                    self.logger.debug(f"Issue with fetching channel: {channel_id=}, {bet=}")
                    continue

                message = channel.get_partial_message(message_id)

                embed = self.embed_manager.get_bet_embed(guild, bet["bet_id"], bet)
                view = BetView(bet, self.place, self.close)
                await message.edit(embed=embed, view=view)

            self.bot.add_view(LeaderBoardView(self.embed_manager))

            self.logger.info("Trying to do the git thing")
            try:
                commit_log = self.git_compare(guild.id)
                self.logger.info("Got commit log successfully")

                if commit_log is not None:
                    if guild.id == BSE_SERVER_ID:
                        channel_id = BSEDDIES_REVOLUTION_CHANNEL
                    else:
                        # should get channel from server collection
                        # TODO: #79
                        channel_id = 291508460519161856

                    channel = await guild.fetch_channel(channel_id)

                    update_message = (
                        "I have just been updated and restarted. Here are the recent commits in this new update:\n\n"
                        "```diff\n"
                        f"{commit_log}\n"
                        "```"
                    )
                    try:
                        # await channel.send(content=update_message)
                        self.logger.info("Not sending message...")
                        self.logger.info(update_message)
                    except discord.errors.HTTPException:
                        self.logger.info("Message is too long to send - skipping")
            except Exception as e:
                self.logger.exception(f"Error with doing the git thing: {e}")
            self.logger.info(f"Finishing checking {guild.name}")

        self.finished = True

    @guild_checker.before_loop
    async def before_guild_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
        while not self.on_ready.finished:
            self.logger.info("Waiting for on_ready to complete")
            await asyncio.sleep(5)

    def git_compare(self, guild_id: int) -> Optional[str]:
        """Returns

        Returns:
        """
        if guild_id == BSE_SERVER_ID:
            path = "/home/app"
        else:
            if os.name == "posix":
                path = os.path.expanduser("~/gitwork/bsebot/bsebot.git")
            else:
                path = os.path.expanduser("~/gitwork/bsebot")

        hash_doc = self.hashes.get_last_hash(guild_id)
        try:
            last_hash = hash_doc["hash"]
        except TypeError:
            # typically in testing mode - there's no hash doc to compare against
            return None

        try:
            head_sha = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=path
                ).decode("utf8").strip("\n")
        except NotADirectoryError:
            self.logger.info(f"Got an error with the directory: {path}")
            return None

        self.logger.info(f"{head_sha=}")

        if last_hash == head_sha:
            self.logger.info(f"{last_hash=}, {head_sha=}")
            return None

        if guild_id == BSE_SERVER_ID:
            path = "/home/gitwork/bsebot"

        commit_log = subprocess.check_output([
            "git",
            "log",
            f"{last_hash}..{head_sha}"
        ], cwd=path).decode("utf8").strip("\n")

        self.logger.info(f"{commit_log=}")

        # set the commit hash now
        self.hashes.update({"_id": hash_doc["_id"]}, {"$set": {"hash": head_sha}})

        return commit_log
