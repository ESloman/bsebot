"""Our Marvel AD message action."""

import datetime
import random
import re
from zoneinfo import ZoneInfo

import discord

from discordbot.bsebot import BSEBot
from discordbot.constants import MARVEL_AD_COOLDOWN
from discordbot.message_actions.base import BaseMessageAction


class MarvelComicsAdAction(BaseMessageAction):
    """Marvel comic add message action."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
        """
        super().__init__(client)

        self._comic_terms = [
            "comic",
            "comics",
            "marvel",
        ]

    async def pre_condition(self, message: discord.Message, _: list[str]) -> bool:
        """Marvel comics ad precondition.

        Checks that the message contains our triggers and that it's mean more than the cooldown since the
        last time we sent an ad.

        Args:
            message (discord.Message): message to check
            _ (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if any(re.findall(rf"\b{a}\b", message.content.lower()) for a in self._comic_terms):
            # check last time that we sent a marvel comic ad
            now = datetime.datetime.now(tz=ZoneInfo("UTC"))
            _last_time = self.guilds.get_last_ad_time(message.guild.id)
            if _last_time and (now - _last_time).total_seconds() < MARVEL_AD_COOLDOWN:
                return False
            # still make it a 50/50 to trigger
            if random.random() > 0.5:  # noqa: PLR2004
                self.guilds.set_last_ad_time(message.guild.id, now)
                return True
        return False

    @staticmethod
    async def run(message: discord.Message) -> None:
        """Marvel ad action.

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
