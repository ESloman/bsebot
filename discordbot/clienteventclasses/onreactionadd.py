"""Contains our OnReactionAdd class.

Handles on_reaction and on_raw_reaction_add events.
"""

import datetime
import logging
from zoneinfo import ZoneInfo

import discord
from discord.emoji import Emoji

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnReactionAdd(BaseEvent):
    """Class for handling on_reaction_add events from Discord."""

    def __init__(self, client: BSEBot, guild_ids: list[int], logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)

    async def handle_reaction_event(
        self,
        message: discord.Message,
        guild: discord.Guild,
        channel: discord.TextChannel,
        reaction_emoji: str,
        user: discord.User,
    ) -> None:
        """Main event for handling reaction events.

        Firstly, we only care about reactions if they're from users so we discard any bot reactions.

        Secondly, we work out if it's a reaction to a user message or a bot message and handle accordingly.

        Then we check what type of message the user is reacting to and pass it off to the relevant class to handle
        the event

        Args:
            message (discord.Message): the message
            guild (discord.Guild): the guild
            channel (discord.TextChannel): the channel
            reaction_emoji (str): the reaction emoji
            user (discord.User): the user

        Returns:
            None
        """
        if user.bot:
            return None

        if guild.id not in self.guild_ids:
            return None

        return self.handle_user_reaction(reaction_emoji, message, guild, channel, user)

    def handle_user_reaction(
        self,
        reaction: str,
        message: discord.Message,
        guild: discord.Guild,
        channel: discord.TextChannel,
        user: discord.User,
    ) -> None:
        """Handle user reaction.

        Args:
            reaction (str): _description_
            message (discord.Message): _description_
            guild (discord.Guild): _description_
            channel (discord.TextChannel): _description_
            user (discord.User): _description_

        Returns:
            None
        """
        message_id = message.id
        guild_id = guild.id
        author = message.author

        if isinstance(reaction, Emoji | discord.PartialEmoji):
            reaction = reaction.name

        self.interactions.add_reaction_entry(
            message_id,
            guild_id,
            user.id,
            channel.id,
            reaction,
            datetime.datetime.now(tz=ZoneInfo("UTC")),
            author.id,
        )

        emoji_obj = self.server_emojis.get_emoji_from_name(guild_id, reaction)
        if not emoji_obj:
            return

        if user.id == emoji_obj.created_by:
            self.logger.info("user used their own emoji")
            return
        self.interactions.add_entry(
            message_id,
            guild_id,
            emoji_obj.created_by,
            channel.id,
            [
                "emoji_used",
            ],
            reaction,
            datetime.datetime.now(tz=ZoneInfo("UTC")),
            additional_keys={"emoji_id": emoji_obj.eid},
        )
