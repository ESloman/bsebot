
import datetime
import re
from logging import Logger

import discord

from discordbot.bsebot import BSEBot
from discordbot.constants import MARVEL_AD_COOLDOWN
from discordbot.message_actions.base import BaseMessageAction


class MarvelComicsAdAction(BaseMessageAction):
    """
    Marvel comic add message action
    """
    def __init__(self, client: BSEBot, logger: Logger) -> None:
        super().__init__(client, logger)

        self._comic_terms = [
            "comic",
            "comics",
            "marvel",
        ]

    async def pre_condition(self, message: discord.Message, message_type: list) -> bool:
        """
        Marvel comics ad precondition
        Checks that the message contains our triggers and that it's mean more than the cooldown since the
        last time we sent an ad

        Args:
            message (discord.Message): message to check
            message_type (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if any([re.match(rf"\b{a}\b", message.content.lower()) for a in self._comic_terms]):
            # check last time that we sent a marvel comic ad
            now = datetime.datetime.now()
            _last_time = self.guilds.get_last_ad_time(message.guild.id)
            if _last_time:
                if (now - _last_time).total_seconds() < MARVEL_AD_COOLDOWN:
                    return False
            self.guilds.set_last_ad_time(message.guild.id, now)
            return True
        return False

    async def run(self, message: discord.Message) -> None:
        """Marvel ad action

        Args:
            message (discord.Message): the message to action
        """

        msg = (
            "**A World of Comics Awaits.\n\n**"
            "Get access to tens of thousands of Marvel comics for under a tenner a month!\n"
            "Try for _free_ for _7_ days and then "
            "get _50%_ off your first two months with code **BSEBOT**.\n\n"
            "https://www.marvel.com/unlimited\n\n"
            "**#AD**"
        )

        await message.reply(content=msg, suppress=True)
