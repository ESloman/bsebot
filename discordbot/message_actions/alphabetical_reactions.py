"""Alphabetical message action class."""

from logging import Logger

import discord

from discordbot.bsebot import BSEBot
from discordbot.message_actions.base import BaseMessageAction


class AlphabeticalMessageAction(BaseMessageAction):
    """Aplhabetical message action class for adding reactions to alphabetical messages."""

    def __init__(self, client: BSEBot, logger: Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
            logger (Logger): our logger
        """
        super().__init__(client, logger)

    @staticmethod
    async def pre_condition(message: discord.Message, _: list[str]) -> bool:
        """Alphabetical precondition. Checks that a message is alphabetical.

        Args:
            message (discord.Message): message to check
            _ (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if not message.content:
            return False
        content = message.content.lower()
        for punc in [".", "?", "!", ":", ";", '"', "'", "£", "%", "&", "(", ")"]:
            content = content.replace(punc, "")
        message_parts = content.split()
        if len(message_parts) < 4:  # noqa: PLR2004
            # don't count short messages
            return False
        sorted_message_parts = sorted(message_parts)
        return message_parts == sorted_message_parts

    async def run(self, message: discord.Message) -> None:
        """Add 'abc' reaction.

        Args:
            message (discord.Message): the message to action
        """
        await message.add_reaction("🔤")
        self.user_interactions.update({"message_id": message.id}, {"$push": {"message_type": "alphabetical"}})
