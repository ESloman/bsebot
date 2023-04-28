
import random
import re
from logging import Logger

import discord

from discordbot.bsebot import BSEBot
from discordbot.message_actions.base import BaseMessageAction


class BirthdayReplies(BaseMessageAction):
    """
    Message action class for handling birthday reply messages for the bot
    """
    def __init__(self, client: BSEBot, logger: Logger) -> None:
        super().__init__(client, logger)
        self._birthday_terms = [
            "happy birthday",
            "hb"
        ]
        self._bot_terms = [
            "bsebot",
            "bse bot",
            "bot"
        ]
        self._possible_replies = [
            "Thank you ❤️"
        ]
        self._possible_reactions = [
            "🥰",
            "❤️",
            "😍",
        ]

    async def pre_condition(self, message: discord.Message, message_type: list) -> bool:
        """
        Precondition that checks whether or not the message is a 'happy birthday' style
        message for our bot on it's birthday.

        Args:
            message (discord.Message): the message to check
            message_type (list): pre-calculated message_type to help with condition

        Returns:
            bool: whether or not to run this action on this message
        """
        if message.created_at.month != 2 or message.created_at.day != 14:
            # only trigger on bot's birthday
            return False
        mentions_ids = [m.id for m in message.mentions]
        send_message = False
        if any([re.match(rf"\b{a}\b", message.content.lower()) for a in self._birthday_terms]):
            if self.client.user.id in mentions_ids:
                # we were mentioned!
                send_message = True
            elif any([re.match(rf"\b{a}\b", message.content.lower()) for a in self._bot_terms]):
                send_message = True
            elif message.reference:
                _reply = message.reference.cached_message
                if not _reply:
                    channel = await self.client.fetch_channel(message.reference.channel_id)
                    _reply = await channel.fetch_message(message.reference.message_id)
                if self.client.user.id == _reply.author.id:
                    send_message = True
        return send_message

    async def run(self, message: discord.Message) -> None:
        """
        Action that will either react or send a reply on the message.

        Args:
            message (discord.Message): the message to action on
        """
        await message.channel.trigger_typing()

        if random.random() > 0.5:
            await message.reply(content=random.choice(self._possible_replies))
        else:
            await message.add_reaction(random.choice(self._possible_reactions))
