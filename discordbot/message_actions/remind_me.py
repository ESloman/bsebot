"""Remind me message action class."""

import datetime
import re
from logging import Logger

import discord
import pytz

from discordbot.bsebot import BSEBot
from discordbot.constants import REMIND_ME_COOLDOWN
from discordbot.message_actions.base import BaseMessageAction


class RemindMeAction(BaseMessageAction):
    """Remind Me message action.

    Suggests to users to use the bot's remind me functionality.
    """

    def __init__(self, client: BSEBot, logger: Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
            logger (Logger): our logger
        """
        super().__init__(client, logger)

        self._reminder_terms = [
            "remind me",
            "remindme",
            "need a reminder",
        ]

    async def pre_condition(self, message: discord.Message, _: list) -> bool:
        """Remind me precondition.

        Checks that the message contains our triggers and that it's mean more than the cooldown since the
        last time we sent a reminder.

        Args:
            message (discord.Message): message to check
            _ (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if any(re.match(rf"\b{a}\b", message.content.lower()) for a in self._reminder_terms):
            # check last time that we sent a marvel comic ad
            now = datetime.datetime.now(tz=pytz.utc)
            _last_time = self.guilds.get_last_remind_me_time(message.guild.id)
            if _last_time and (now - _last_time).total_seconds() < REMIND_ME_COOLDOWN:
                return False
            self.guilds.set_last_remind_me_time(message.guild.id, now)
            return True
        return False

    @staticmethod
    async def run(message: discord.Message) -> None:
        """Remind me action.

        Args:
            message (discord.Message): the message to action
        """
        msg = (
            "# Looking for a reminder?\n"
            "Use `/remindme` to set a new reminder in Discord.\n"
            "_Or_, to be reminded about an existing message:"
            "\n- right-click the message"
            "\n- press *Apps*"
            "\n- press *Remind me*"
            "\n\n"
            "To see other commands, use `/help`."
        )

        await message.reply(content=msg, suppress=True)
