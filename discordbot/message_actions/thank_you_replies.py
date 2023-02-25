
import random
import re

import discord

from discordbot.message_actions.base import BaseMessageAction


class ThankYouReplies(BaseMessageAction):
    """
    Message action class for sending thank you messages
    """
    def __init__(self, client: discord.Bot) -> None:
        super().__init__(client)
        self._thank_you_terms = [
            "thank you",
            "thanks",
            "ty",
            "cutie",
            "i love you",
        ]
        self._bot_terms = [
            "bsebot",
            "bse bot"
        ]
        self._possible_replies = [
            "You are most welcome.",
            "Your praise means everything to me.",
            "I exist to serve.",
            "Thank you ❤️",
            "You're welcome!",
            "Anytime cute stuff.",
            "No worries!",
            "I am happy to assist.",
            "I am happy that you're happy!",
            "https://media.giphy.com/media/tXTqLBYNf0N7W/giphy.gif",
            "https://media.giphy.com/media/l41lY4I8lZXH0vIe4/giphy.gif",
            "https://media.giphy.com/media/1qfb3aFqldWklPQwS3/giphy.gif",
            "https://media.giphy.com/media/e5nATuISYAZ4Q/giphy.gif",
            "https://media.giphy.com/media/xT0Cyhi8GCSU91PvtC/giphy.gif",
        ]
        self._possible_reactions = [
            "🥰",
            "❤️",
            "😍",
        ]

    async def pre_condition(self, message: discord.Message, message_type: list) -> bool:
        """
        Checks that any of the 'thank you' terms are in the message
        If they are, checks that we were mentioned or it's about the bot
        Returns true if so, False if not

        Args:
            message (discord.Message): the message to action
            message_type (list): the pre-calculated message_type

        Returns:
            bool: whether to send the message or not
        """
        mentions_ids = [m.id for m in message.mentions]
        send_message = False
        if any([re.match(rf"\b{a}\b", message.content.lower()) for a in self._thank_you_terms]):
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
        Sends either a reaction or a reply (random) with a random emoji/reply text

        Args:
            message (discord.Message): the message to reply to
        """
        await message.channel.trigger_typing()

        if random.random() > 0.5:
            await message.reply(content=random.choice(self._possible_replies))
        else:
            await message.add_reaction(random.choice(self._possible_reactions))
