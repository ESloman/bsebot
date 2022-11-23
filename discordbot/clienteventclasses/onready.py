import datetime
import os
import subprocess
from typing import Optional

import discord

from discordbot.baseeventclass import BaseEvent
from discordbot.bot_enums import TransactionTypes, ActivityTypes
from discordbot.constants import BSEDDIES_REVOLUTION_CHANNEL, THE_BOYS_ROLE, BSE_SERVER_ID, GENERAL_CHAT
from discordbot.slashcommandeventclasses import BSEddiesPlaceBet, BSEddiesCloseBet
from discordbot.views import LeaderBoardView, RevolutionView, BetView
from mongo.bsedataclasses import CommitHash, SpoilerThreads
from mongo.bseticketedevents import RevolutionEvent
from mongo.bsepoints import UserInteractions, ServerEmojis


class OnReadyEvent(BaseEvent):
    """
    Class for handling on_ready event
    """
    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.server_emojis = ServerEmojis()
        self.user_interactions = UserInteractions()
        self.events = RevolutionEvent()
        self.close = BSEddiesCloseBet(client, guild_ids, self.logger)
        self.place = BSEddiesPlaceBet(client, guild_ids, self.logger)
        self.spoilers = SpoilerThreads()
        self.hashes = CommitHash()

    async def on_ready(self) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """
        self.logger.info("Beginning OnReady sequence")

        self.logger.info("Syncing commands")
        await self.client.sync_commands(method="auto", guild_ids=self.guild_ids)
        self.logger.info("Synced commands")

        messages_to_delete = [
            # ( message_id , channel_id )
        ]

        for guild_id in self.guild_ids:
            guild = self.client.get_guild(guild_id)  # type: discord.Guild
            self.logger.info(f"Checking guild: {guild.id} - {guild.name}")

            self.logger.info("Checking guilds for new members")
            for member in guild.members:  # type: discord.Member
                if member.bot:
                    continue

                self.logger.info(f"Checking {member.id} - {member.name}")
                user = self.user_points.find_user(member.id, guild.id)
                if not user:

                    the_boys_role = [role for role in member.roles if role == THE_BOYS_ROLE]

                    self.user_points.create_user(member.id, guild.id, bool(the_boys_role))
                    self.logger.info(
                        f"Creating new user entry for {member.id} - {member.name} for {guild.id} - {guild.name}"
                    )

                    self.user_points.append_to_transaction_history(
                        member.id,
                        guild.id,
                        {
                            "type": TransactionTypes.USER_CREATE,
                            "amount": 10,
                            "timestamp": datetime.datetime.now(),
                            "comment": "User created",
                        }
                    )
                    continue

                if not user.get("daily_eddies"):
                    the_boys_role = [role for role in member.roles if role == THE_BOYS_ROLE]
                    self.user_points.set_daily_eddies_toggle(member.id, guild.id, bool(the_boys_role))

            self.logger.info("Checking for users that have left")
            member_ids = [member.id for member in guild.members]
            _users = self.user_points.get_all_users_for_guild(guild_id)
            _users = [u for u in _users if not u.get("inactive")]
            for user in _users:
                if user["uid"] not in member_ids:

                    self.user_points.update({"_id": user["_id"]}, {"$set": {"inactive": True}})
                    self.user_points.append_to_activity_history(
                        user["uid"],
                        guild_id,
                        {
                            "type": ActivityTypes.SERVER_LEAVE,
                            "timestamp": datetime.datetime.now()
                        }
                    )

            self.logger.info("Checking guild emojis")
            await guild.fetch_emojis()
            # sort out emojis
            for emoji in guild.emojis:
                emoji_obj = await guild.fetch_emoji(emoji.id)
                emoji_db_obj = self.server_emojis.get_emoji(guild_id, emoji_obj.id)
                if not emoji_db_obj:
                    self.logger.info(f"{emoji_obj.name} doesn't exist in the DB yet - inserting")
                    self.server_emojis.insert_emoji(
                        emoji_obj.id,
                        emoji_obj.name,
                        emoji_obj.created_at,
                        emoji_obj.user.id,
                        guild_id
                    )

                    # give user eddies retroactively for reacting custom emojis
                    self.user_interactions.add_entry(
                        emoji_obj.id,
                        guild_id,
                        emoji_obj.user.id,
                        guild_id,
                        ["emoji_created", ],
                        emoji_obj.name,
                        datetime.datetime.now(),
                        additional_keys={"emoji_id": emoji_obj.id, "created_at": emoji_obj.created_at}
                    )

            self.logger.info("Checking guild stickers")
            await guild.fetch_stickers()
            # sort out stickers
            for sticker in guild.stickers:
                stick_obj = await guild.fetch_sticker(sticker.id)
                sticker_db_obj = self.server_stickers.get_sticker(guild_id, stick_obj.id)
                if not sticker_db_obj:
                    self.logger.info(f"{stick_obj.name} doesn't exist in the DB yet - inserting")
                    self.server_stickers.insert_sticker(
                        stick_obj.id,
                        stick_obj.name,
                        stick_obj.created_at,
                        stick_obj.user.id,
                        guild_id
                    )

                    # give user eddies retroactively for reacting custom emojis
                    self.user_interactions.add_entry(
                        stick_obj.id,
                        guild_id,
                        stick_obj.user.id,
                        guild_id,
                        ["sticker_created", ],
                        stick_obj.name,
                        datetime.datetime.now(),
                        additional_keys={"sticker_id": stick_obj.id, "created_at": stick_obj.created_at}
                    )

            # join all threads
            self.logger.info("Joining threads")
            for channel in guild.channels:
                if type(channel) not in [discord.channel.TextChannel]:
                    continue

                if threads := channel.threads:
                    for thread in threads:
                        if thread.archived or thread.locked:
                            continue

                        await thread.fetch_members()

                        if self.client.user.id not in [member.id for member in thread.members]:

                            await thread.join()
                            self.logger.info(f"Joined {thread.name}")

            # add thread to spoiler info
            self.logger.info("Checking spoiler threads")
            if guild_id == BSE_SERVER_ID:
                general = await guild.fetch_channel(GENERAL_CHAT)
                if threads := general.threads:
                    for thread in threads:
                        thread_id = thread.id
                        thread_info = self.spoilers.get_thread_by_id(BSE_SERVER_ID, thread_id)

                        if not thread_info:
                            self.logger.info(f"No info for thread {thread_id}, {thread.name}. Inserting now.")
                            self.spoilers.insert_spoiler_thread(
                                BSE_SERVER_ID,
                                thread_id,
                                thread.name,
                                thread.created_at,
                                thread.owner_id
                            )

            self.logger.info("Initialising event views")
            if events := self.events.get_open_events(guild_id):
                if len(events) > 1:
                    self.logger.info("???")
                    continue
                event = events[0]
                view = RevolutionView(self.client, event, self.logger)
                view.toggle_stuff(False)
                self.client.add_view(view)
                message_id = event["message_id"]
                channel_id = event["channel_id"]

                channel = await guild.fetch_channel(channel_id)
                message = channel.get_partial_message(message_id)

            # find all open bets
            self.logger.info("Initialising bet views")
            bets = self.user_bets.get_all_active_bets(guild_id)
            other_bets = self.user_bets.get_all_inactive_pending_bets(guild_id)
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

            self.logger.info("Deleting messages")
            try:
                for message in messages_to_delete:
                    channel = await guild.fetch_channel(message[1])
                    message_obj = channel.get_partial_message(message[0])
                    await channel.delete_messages([message_obj, ])
            except (discord.errors.InvalidData, discord.errors.NotFound):
                pass

            self.client.add_view(LeaderBoardView(self.embed_manager))

            self.logger.info("Trying to do the git thing")
            try:
                commit_log = self.git_compare(guild_id)
                self.logger.info("Got commit log successfully")

                if commit_log is not None:
                    if guild_id == BSE_SERVER_ID:
                        channel_id = BSEDDIES_REVOLUTION_CHANNEL
                    else:
                        channel_id = 291508460519161856

                    channel = await guild.fetch_channel(channel_id)

                    update_message = (
                        "I have just been updated and restarted. Here are the recent commits in this new update:\n\n"
                        "```diff\n"
                        f"{commit_log}\n"
                        "```"
                    )
                    try:
                        await channel.send(content=update_message)
                    except discord.errors.HTTPException:
                        self.logger.info("Message is too long to send - skipping")
            except Exception as e:
                self.logger.exception(f"Error with doing the git thing: {e}")

            self.logger.info(f"Finishing checking {guild_id}")

        self.logger.info("Finished OnReady sequence")

    def git_compare(self, guild_id: int) -> Optional[str]:
        """Returns

        Returns:
            str: _description_
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
