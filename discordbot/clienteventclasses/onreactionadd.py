import datetime

import discord
from discord.emoji import Emoji

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from mongo.bsepoints import UserInteractions


class OnReactionAdd(BaseEvent):
    """
    Class for handling on_reaction_add events from Discord
    """
    def __init__(self, client, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
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

        return self.handle_user_reaction(reaction_emoji, message, guild, channel, user, message.author)

    def handle_user_reaction(
            self,
            reaction: str,
            message: discord.Message,
            guild: discord.Guild,
            channel: discord.TextChannel,
            user: discord.User,
            author: discord.Member
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
            if user.id == emoji_obj["created_by"]:
                self.logger.info("user used their own emoji")
                return
            self.user_interactions.add_entry(
                message_id,
                guild_id,
                emoji_obj["created_by"],
                channel.id,
                ["emoji_used", ],
                reaction,
                datetime.datetime.now(),
                additional_keys={"emoji_id": emoji_obj["eid"]}
            )
