"""Rigged message action class."""

import re

import discord

from discordbot.bsebot import BSEBot
from discordbot.constants import RIGGED_COOLDOWN
from discordbot.message_actions.base import BaseMessageAction


class RiggedAction(BaseMessageAction):
    """Rigged action."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
        """
        super().__init__(client)

    async def pre_condition(self, message: discord.Message, _: list[str]) -> bool:
        """Rigged action message action.

        Works out if the message contains "rigged" and is recently after a revolution.

        Args:
            message (discord.Message): message to check
            _ (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        guild_db = self.guilds.get_guild(message.guild.id)
        if message.channel.id != guild_db.channel:
            return False

        if (
            any(re.findall(r"\brigged\b", message.content.lower()))
            and guild_db.last_revolution_time
            and 0 < (message.created_at - guild_db.last_revolution_time).total_seconds() <= 900  # noqa: PLR2004
        ):
            # been less than fifteen minutes since last revolution
            last_rigged_time = guild_db.last_rigged_time
            if not last_rigged_time or (message.created_at - last_rigged_time).total_seconds() >= RIGGED_COOLDOWN:
                return True

        return False

    async def run(self, message: discord.Message) -> None:
        """Rigged action, sends the 'RiGgEd' meme.

        Args:
            message (discord.Message): the message to action
        """
        self.guilds.set_last_rigged_time(message.guild.id)

        msg = "https://i.imgur.com/vx4i1XM.jpg"

        await message.reply(content=msg)
