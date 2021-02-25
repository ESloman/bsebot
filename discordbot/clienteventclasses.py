import datetime
import logging
import re
from typing import Union

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserPoints, UserInteractions


class BaseEvent(object):
    """
    This is a BaseEvent class that all events will inherit from.

    Basically just sets up all the vars that events will need and rely on.
    """
    def __init__(self,
                 client: discord.Client,
                 guild_ids: list,
                 logger: logging.Logger,
                 beta_mode: bool = False):
        """
        Constructor that initialises references DB Collections and various variables
        :param client:
        :param guild_ids:
        :param logger:
        :param beta_mode:
        """
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.client = client
        self.guild_ids = guild_ids
        self.beta_mode = beta_mode
        self.embed_manager = EmbedManager(logger)
        self.logger = logger


class OnReadyEvent(BaseEvent):
    """
    Class for handling on_ready event
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def on_ready(self) -> None:
        """
        Method called for on_ready event. Makes sure we have an entry for every user in each guild.
        :return: None
        """
        self.logger.info("Checking guilds for members")

        for guild_id in self.guild_ids:
            guild = self.client.get_guild(guild_id)
            self.logger.info(f"Checking guild: {guild.id} - {guild.name}")
            for member in guild.members:
                if not member.bot:
                    self.logger.info(f"Checking {member.id} - {member.name}")
                    user = self.user_points.find_user(member.id, guild.id)
                    if not user:
                        self.user_points.create_user(member.id, guild.id)
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

                    elif "pending_points" not in user:
                        self.user_points.set_pending_points(member.id, guild.id, 0)
                        self.logger.info(f"Setting pending points to 0 for {member.name}")

        self.logger.info("Finished member check.")


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

        self.logger.info(f"Creating BSEddies account for new user - {user_id} - {member.display_name}")


class OnReactionAdd(BaseEvent):
    """
    Class for handling on_reaction_add events from Discord
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

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

        Secondly, we only care about reactions to bot messages at the moment so discard any other events.

        Then we check what type of message the user is reacting to:

          - if it's a 'Leaderboard' message then we update the message with the full updated rankings
          - if it's a 'BET' message then we check the bet is active and that the user is betting with a valid emoji.
            If that's both fine then we call the function to add the bet to the actual BET. That function will do some
            additional checking so we don't need to do loads of validation here.

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

        if not message.author.bot:
            return

        # handling leaderboard messages
        if message.content and "BSEddies Leaderboard" in message.content and reaction_emoji == u"▶️":
            if not message.author.bot:
                return

            content = self.embed_manager.get_leaderboard_embed(guild, None)
            await message.edit(content=content)
            return

        # handling reactions to BETS
        if message.embeds and "Bet ID" in message.embeds[0].description:
            embed = message.embeds[0]  # type: discord.Embed
            bet_id = re.findall(r"(?<=Bet ID: )\d\d\d\d", embed.description)[0]
            bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

            link = f"https://discordapp.com/channels/{guild.id}/{channel.id}/{message.id}"

            # make sure the bet is active
            if not bet["active"]:
                msg = f"Your reaction on **Bet {bet_id}** _(<{link}>)_ failed as the bet is closed for new bets."
                if not user.dm_channel:
                    await user.create_dm()
                try:
                    await user.send(content=msg)
                except discord.errors.Forbidden:
                    pass
                await message.remove_reaction(reaction_emoji, user)
                return

            # make sure that the reaction is a valid outcome
            if reaction_emoji not in bet['option_dict']:
                msg = f"Your reaction on **Bet {bet_id}** _(<{link}>)_ failed as that reaction isn't a valid outcome."
                if not user.dm_channel:
                    await user.create_dm()
                try:
                    await user.send(content=msg)
                except discord.errors.Forbidden:
                    pass
                await message.remove_reaction(reaction_emoji, user)
                return

            # do the bet
            ret = self.user_bets.add_better_to_bet(bet_id, guild.id, user.id, reaction_emoji, 1)

            if ret["success"]:
                new_bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
                embed = self.embed_manager.get_bet_embed(guild, bet_id, new_bet)

                await message.edit(embed=embed)

                # add to transaction history
                self.user_points.append_to_transaction_history(
                    user.id,
                    guild.id,
                    {
                        "type": TransactionTypes.BET_PLACE,
                        "amount": -1,
                        "timestamp": datetime.datetime.now(),
                        "bet_id": bet_id,
                        "comment": "Bet placed through reaction",
                    }
                )

            await message.remove_reaction(reaction_emoji, user)


class OnMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)
        self.user_interactions = UserInteractions()

    async def message_received(self, message: discord.Message):
        """
        Main method for handling when we receive a message.
        Mostly just extracts data and puts it into the DB.
        We also work out what "type" of message it is.
        :param message:
        :return:
        """

        guild_id = message.guild.id
        user_id = message.author.id
        channel_id = message.channel.id
        message_content = message.content

        if guild_id not in self.guild_ids:
            return

        if message.reference:
            message_type = "reply"
        elif message.attachments:
            message_type = "attachment"
        elif message.role_mentions:
            message_type = "role_mention"
        elif message.channel_mentions:
            message_type = "channel_mention"
        elif message.mentions:
            message_type = "mention"
        elif message.mention_everyone:
            message_type = "everyone_mention"
        elif "https://" in message.content or "http://" in message_content:
            if "gif" in message.content:
                message_type = "gif"
            else:
                message_type = "link"
        else:
            message_type = "message"

        self.user_interactions.add_entry(
            message.id,
            guild_id,
            user_id,
            channel_id,
            message_type,
            message_content,
            message.created_at
        )
