import datetime
import os
import re
import subprocess
from typing import List, Optional

import discord
from discord.emoji import Emoji

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
    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.server_emojis = ServerEmojis()
        self.user_interactions = UserInteractions()
        self.events = RevolutionEvent()
        self.close = BSEddiesCloseBet(client, guild_ids, self.logger, self.beta_mode)
        self.place = BSEddiesPlaceBet(client, guild_ids, self.logger, self.beta_mode)
        self.spoilers = SpoilerThreads()
        self.hashes = CommitHash()

    async def on_ready(self) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """
        self.logger.info("Checking guilds for members")

        messages_to_delete = [
            # ( message_id , channel_id )
        ]

        for guild_id in self.guild_ids:
            guild = self.client.get_guild(guild_id)  # type: discord.Guild
            self.logger.info(f"Checking guild: {guild.id} - {guild.name}")
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

            await guild.fetch_emojis()
            # sort out emojis
            for emoji in guild.emojis:
                emoji_obj = await guild.fetch_emoji(emoji.id)
                emoji_db_obj = self.server_emojis.get_emoji(guild_id, emoji_obj.id)
                if not emoji_db_obj:
                    print(f"{emoji_obj.name} doesn't exist in the DB yet - inserting")
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
                        {"emoji_id": emoji_obj.id, "created_at": emoji_obj.created_at}
                    )

            await guild.fetch_stickers()
            # sort out stickers
            for sticker in guild.stickers:
                stick_obj = await guild.fetch_sticker(sticker.id)
                sticker_db_obj = self.server_stickers.get_sticker(guild_id, stick_obj.id)
                if not sticker_db_obj:
                    print(f"{stick_obj.name} doesn't exist in the DB yet - inserting")
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
                        {"sticker_id": stick_obj.id, "created_at": stick_obj.created_at}
                    )

            # join all threads
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
                            print(f"Joined {thread.name}")

            # add thread to spoiler info
            if guild_id == BSE_SERVER_ID:
                general = await guild.fetch_channel(GENERAL_CHAT)
                if threads := general.threads:
                    for thread in threads:
                        thread_id = thread.id
                        thread_info = self.spoilers.get_thread_by_id(BSE_SERVER_ID, thread_id)

                        if not thread_info:
                            print(f"No info for thread {thread_id}, {thread.name}. Inserting now.")
                            self.spoilers.insert_spoiler_thread(
                                BSE_SERVER_ID,
                                thread_id,
                                thread.name,
                            )

            if events := self.events.get_open_events(guild_id):
                if len(events) > 1:
                    print(f"???")
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
            bets = self.user_bets.get_all_active_bets(guild_id)
            for bet in bets:
                message_id = bet["message_id"]
                channel_id = bet["channel_id"]
                channel = await guild.fetch_channel(channel_id)

                message = channel.get_partial_message(message_id)

                embed = self.embed_manager.get_bet_embed(guild, bet["bet_id"], bet)
                view = BetView(bet, self.place, self.close)
                await message.edit(embed=embed, view=view)

            try:
                for message in messages_to_delete:
                    channel = await guild.fetch_channel(message[1])
                    message_obj = channel.get_partial_message(message[0])
                    await channel.delete_messages([message_obj, ])
            except (discord.errors.InvalidData, discord.errors.NotFound):
                pass

            self.client.add_view(LeaderBoardView(self.embed_manager))

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
                await channel.send(content=update_message)

        self.logger.info("Finished member check.")

    def git_compare(self, guild_id: int) -> Optional[str]:
        """Returns

        Returns:
            str: _description_
        """
        if guild_id == BSE_SERVER_ID:
            path = "/home/app"
        else:
            path = os.path.expanduser("~/gitwork/bsebot/bsebot.git")
        
        hash_doc = self.hashes.get_last_hash(guild_id)
        last_hash = hash_doc["hash"]
        
        head_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=path
            ).decode("utf8").strip("\n")
        self.logger.info(f"{head_sha=}")
        
        if last_hash == head_sha:
            return None
        
        commit_log = subprocess.check_output([
            "git",
            "log",
            f"{last_hash}..{head_sha}"
        ], cwd=path).decode("utf8").strip("\n")

        self.logger.info(f"{commit_log=}")
        
        # set the commit hash now
        self.hashes.update({"_id": hash_doc["_id"]}, {"$set": {"hash": head_sha}})

        return commit_log


class OnMemberJoin(BaseEvent):
    """
    Class for handling when a new member joins the server
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    def on_join(self, member: discord.Member) -> None:
        """
        Method for handling when a new member joins the server.
        We basically just make sure that the user has an entry in our DB
        :param member:
        :return: None
        """
        user_id = member.id

        if user := self.user_points.find_user(user_id, member.guild.id):
            self.user_points.update({"_id": user["_id"]}, {"$set": {"inactive": False}})
            self.logger.info(f"Activating BSEddies account for existing user - {user_id} - {member.display_name}")
            self.user_points.append_to_activity_history(
                user_id,
                member.guild.id,
                {
                    "type": ActivityTypes.SERVER_JOIN,
                    "timestamp": datetime.datetime.now()
                }
            )
            return

        self.user_points.create_user(user_id, member.guild.id)

        self.user_points.append_to_transaction_history(
            user_id,
            member.guild.id,
            {
                "type": TransactionTypes.USER_CREATE,
                "amount": 10,
                "timestamp": datetime.datetime.now(),
                "comment": "User created",
            }
        )

        self.user_points.append_to_activity_history(
            user_id,
            member.guild.id,
            {
                "type": ActivityTypes.SERVER_JOIN,
                "timestamp": datetime.datetime.now()
            }
        )

        self.logger.info(f"Creating BSEddies account for new user - {user_id} - {member.display_name}")


class OnMemberLeave(BaseEvent):
    """
    Class for handling when a member leaves the server
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    def on_leave(self, member: discord.Member) -> None:
        """
        Method for handling when a member leaves the server.
        We basically just make sure that the user entry is set to inactive
        :param member:
        :return: None
        """
        user_id = member.id

        self.user_points.update({"uid": user_id, "guild_id": member.guild.id}, {"$set": {"inactive": True}})
        self.user_points.append_to_activity_history(
            user_id,
            member.guild.id,
            {
                "type": ActivityTypes.SERVER_LEAVE,
                "timestamp": datetime.datetime.now()
            }
        )
        self.logger.info(f"Deactivating BSEddies account for user - {user_id} - {member.display_name}")
        return


class OnReactionAdd(BaseEvent):
    """
    Class for handling on_reaction_add events from Discord
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def handle_reaction_event(
            self,
            message: discord.Message,
            guild: discord.Guild,
            channel: discord.TextChannel,
            reaction_emoji: str,
            user: discord.User
    ) -> None:
        """
        Main event for handling reaction events.

        Firstly, we only care about reactions if they're from users so we discard any bot reactions.

        Secondly, we work out if it's a reaction to a user message or a bot message and handle accordingly.

        Then we check what type of message the user is reacting to and pass it off to the relevant class to handle
        the event

        :param message:
        :param guild:
        :param channel:
        :param reaction_emoji:
        :param user:
        :return:
        """
        if user.bot:
            return

        if guild.id not in self.guild_ids:
            return

        self.handle_user_reaction(reaction_emoji, message, guild, channel, user, message.author)
        return

    def handle_user_reaction(
            self, reaction: str, message: discord.Message,
            guild: discord.Guild, channel: discord.TextChannel, user: discord.User, author: discord.Member
    ) -> None:
        """

        :param reaction:
        :param message:
        :param guild:
        :param channel:
        :param user:
        :param author:
        :return:
        """
        message_id = message.id
        guild_id = guild.id

        if isinstance(reaction, (Emoji, discord.PartialEmoji)):
            reaction = reaction.name

        self.user_interactions.add_reaction_entry(
            message_id,
            guild_id,
            user.id,
            channel.id,
            reaction,
            datetime.datetime.now(),
            author.id
        )

        if emoji_obj := self.server_emojis.get_emoji_from_name(guild_id, reaction):
            if author.id == emoji_obj["created_by"]:
                print("user used their own emoji")
                pass
            self.user_interactions.add_entry(
                message_id,
                guild_id,
                emoji_obj["created_by"],
                channel.id,
                ["emoji_used", ],
                reaction,
                datetime.datetime.now(),
                {"emoji_id": emoji_obj["eid"]}
            )


class OnMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def message_received(self, message: discord.Message, message_type_only=False):
        """
        Main method for handling when we receive a message.
        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.
        :param message:
        :param message_type_only:
        :return:
        """

        guild_id = message.guild.id
        user_id = message.author.id
        channel_id = message.channel.id
        message_content = message.content

        if guild_id not in self.guild_ids:
            return

        message_type = []

        if message.reference:
            referenced_message = self.client.get_message(message.reference.message_id)  # type: discord.Message
            if not referenced_message:
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if referenced_message.author.id != user_id:
                message_type.append("reply")
                self.user_interactions.add_reply_to_message(
                    message.reference.message_id, message.id, guild_id, user_id, message.created_at, message_content
                )

        if stickers := message.stickers:
            for sticker in stickers:  # type: discord.StickerItem
                sticker_id = sticker.id
                if sticker_obj := self.server_stickers.get_sticker(guild_id, sticker_id):
                    # used a custom emoji!
                    message_type.append("custom_sticker")

                    if user_id == sticker_obj["created_by"]:
                        return
                    self.user_interactions.add_entry(
                        sticker_obj["stid"],
                        guild_id,
                        sticker_obj["created_by"],
                        channel_id,
                        ["sticker_used", ],
                        message_content,
                        datetime.datetime.now()
                    )

        if message.attachments:
            message_type.append("attachment")

        if role_mentions := message.role_mentions:
            for _ in role_mentions:
                message_type.append("role_mention")

        if channel_mentions := message.channel_mentions:
            for _ in channel_mentions:
                message_type.append("channel_mention")

        if mentions := message.mentions:
            for mention in mentions:
                if mention.id == user_id:
                    continue
                message_type.append("mention")

        if message.mention_everyone:
            message_type.append("everyone_mention")

        if "https://" in message.content or "http://" in message_content:
            if "gif" in message.content:
                message_type.append("gif")
            else:
                message_type.append("link")

        if not message.attachments:
            message_type.append("message")

        if re.match("Wordle \d?\d\d\d \d\/\d\\n\\n", message.content):
            message_type.append("wordle")

        if emojis := re.findall(r"<:[a-zA-Z_0-9]*:\d*>", message.content):
            for emoji in emojis:
                emoji_id = emoji.strip("<").strip(">").split(":")[-1]
                if emoji_obj := self.server_emojis.get_emoji(guild_id, int(emoji_id)):
                    # used a custom emoji!
                    message_type.append("custom_emoji")

                    if user_id == emoji_obj["created_by"]:
                        return
                    self.user_interactions.add_entry(
                        emoji_obj["eid"],
                        guild_id,
                        emoji_obj["created_by"],
                        channel_id,
                        ["emoji_used", ],
                        message_content,
                        datetime.datetime.now()
                    )

        if message_type_only:
            return message_type

        self.user_interactions.add_entry(
            message.id,
            guild_id,
            user_id,
            channel_id,
            message_type,
            message_content,
            message.created_at
        )


class OnDirectMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger, giphyapi, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.giphyapi = giphyapi

        self.thanks = ["thank you", "thanks", "fanks", "fank you", " ty ", "thanks dad"]
        self.rude = ["fuck you", "fuck off", "faggot", "fuckyou"]

    async def dm_received(self, message: discord.Message):
        """
        Main method for handling when someone sends us a DM
        Basically, send a random gif if they say 'thank you'
        :param message:
        :return:
        """
        message_content = message.content

        if [a for a in self.thanks if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("youre welcome")
            await message.author.send(content=gif)
        elif [a for a in self.rude if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("shocked")
            await message.author.send(content=gif)


class OnThreadCreate(BaseEvent):
    """
        Class for handling on_thread_create event
        """

    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()
        self.on_message = OnMessage(client, guild_ids, logger, beta_mode)

    async def on_thread_create(self, thread: discord.Thread) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """

        await thread.join()
        print(f"Joined {thread.name}")

        if not thread.starting_message:
            starting_message = await thread.fetch_message(thread.id)  # type: discord.Message
        else:
            starting_message = thread.starting_message  # type: discord.Message

        message_type = await self.on_message.message_received(starting_message, True)
        message_type.extend("thread_create")

        self.user_interactions.add_entry(
            thread.id,
            thread.guild.id,
            thread.owner_id,
            thread.parent_id,
            message_type,
            starting_message.content,
            thread.created_at
        )


class OnThreadUpdate(BaseEvent):
    """
    Class for handling on_thread_update event
    """

    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def on_update(self, before: discord.Thread, after: discord.Thread):
        """

        :param before:
        :param after:
        :return:
        """

        if before.archived and not after.archived:
            print(f"Thread has been unarchived - joining")
            thread_members = await after.fetch_members()
            member_ids = [member.id for member in thread_members]
            if self.client.user.id not in member_ids:
                await after.join()
                print(f"Joining unarchived thread")


class OnEmojiCreate(BaseEvent):
    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def on_emojis_update(self, guild_id: int, before: List[discord.Emoji], after: List[discord.Emoji]):

        for emoji in after:
            if emoji_obj := self.server_emojis.get_emoji(guild_id, emoji.id):
                # do something here to make sure nothing has changed
                pass
                continue

            print(f"New emoji, {emoji_obj.name}, created!")
            self.server_emojis.insert_emoji(
                emoji.id,
                emoji.name,
                emoji.created_at,
                emoji.user.id,
                guild_id
            )

            self.user_interactions.add_entry(
                emoji.id,
                guild_id,
                emoji.user.id,
                guild_id,
                ["emoji_created", ],
                emoji.name,
                datetime.datetime.now(),
                {"emoji_id": emoji.id, "created_at": emoji.created_at}
            )


class OnStickerCreate(BaseEvent):
    def __init__(self, client: discord.Bot, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def on_stickers_update(
            self,
            guild_id: int,
            before: List[discord.GuildSticker],
            after: List[discord.GuildSticker]
    ):

        for sticker in after:
            if stick_obj := self.server_stickers.get_sticker(guild_id, sticker.id):
                # do something here to make sure nothing has changed
                pass
                continue

            print(f"New sticker, {stick_obj.name}, created!")
            self.server_stickers.insert_sticker(
                sticker.id,
                sticker.name,
                sticker.created_at,
                sticker.user.id,
                guild_id
            )

            self.user_interactions.add_entry(
                sticker.id,
                guild_id,
                sticker.user.id,
                guild_id,
                ["sticker_created", ],
                sticker.name,
                datetime.datetime.now(),
                {"sticker_id": sticker.id, "created_at": sticker.created_at}
            )
