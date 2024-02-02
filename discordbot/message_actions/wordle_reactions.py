"""Wordle message action class."""

import datetime
import re
from logging import Logger

import discord
import pytz
from discord import PartialEmoji
from pymongo.errors import OperationFailure

from discordbot.bsebot import BSEBot
from discordbot.constants import WORDLE_SCORE_REGEX
from discordbot.message_actions.base import BaseMessageAction


class WordleMessageAction(BaseMessageAction):
    """Wordle message action class for adding reactions to wordle messages."""

    _TOUGH_ONE_DAY_LINK = "https://imgur.com/Uk73HPD"

    def __init__(self, client: BSEBot, logger: Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
            logger (Logger): our logger
        """
        super().__init__(client, logger)

    @staticmethod
    async def pre_condition(_: discord.Message, message_type: list[str]) -> bool:
        """Wordle precondition. Checks that we're a wordle message using the precalc message_type.

        Args:
            _ (discord.Message): message to check
            message_type (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        return "wordle" in message_type

    @staticmethod
    async def _handle_adding_squares(message: discord.Message) -> None:
        """Counts and adds wordle square reactions.

        Args:
            message (discord.Message): the mesage
        """
        content = message.content
        if "🟨" not in content:
            # only greens
            await message.add_reaction("🟩")
        elif content.count("🟨") > content.count("🟩"):
            await message.add_reaction("🟨")

    @staticmethod
    async def _handle_symmetry(message: discord.Message) -> None:
        """Works out if the wordle was symmetrical or not.

        Args:
            message (discord.Message): the message
        """
        _, squares = message.content.split("\n\n")
        squares = squares.split("\n")
        squares = [row.strip() for row in squares]
        for row in squares:
            if row[:2] != row[3:][::-1]:
                # not symmetrical
                return
        await message.add_reaction("🪞")

    async def _handle_tough_day_status(self, message: discord.Message) -> None:
        """Checks to see if need to send our 'tough day' message.

        Args:
            message (discord.Message): the message
        """
        now = datetime.datetime.now(tz=pytz.utc)
        today = now.replace(hour=0, minute=0, second=0)

        # get number of 6/6 or X/6 wordles today
        try:
            wordle_results = self.user_interactions.query(
                {
                    "guild_id": message.guild.id,
                    "is_bot": False,
                    "$text": {"$search": "Wordle 6/6"},
                    "timestamp": {"$gte": today},
                    "message_type": "wordle",
                },
            )
            wordle_results = [r for r in wordle_results if any(a in r["content"] for a in ["6/6", "X/6"])]
        except OperationFailure:
            # text index not set correctly
            return

        if len(wordle_results) < 3:  # noqa: PLR2004
            # exit early - not sent enough wordles to day to send the link
            return

        # make sure we haven't sent this today already
        try:
            link_results = self.user_interactions.query(
                {
                    "guild_id": message.guild.id,
                    "is_bot": True,
                    "$text": {"$search": self._TOUGH_ONE_DAY_LINK},
                    "timestamp": {"$gte": today},
                    "message_type": "link",
                },
            )
            link_results = [r for r in link_results if r["content"] == self._TOUGH_ONE_DAY_LINK]
        except OperationFailure:
            # text index not set correctly
            return

        if len(link_results) > 0:
            self.logger.info("already sent wordle tough image link")
            return

        await message.channel.send(content=self._TOUGH_ONE_DAY_LINK, silent=True)

    async def run(self, message: discord.Message) -> None:
        """Wordle react/reply action.

        Adds a reaction or reply.

        Args:
            message (discord.Message): the message to action
        """
        guild_id = message.guild.id
        result = re.search(WORDLE_SCORE_REGEX, message.content).group()
        guesses = result.split("/")[0]

        await self._handle_adding_squares(message)
        await self._handle_symmetry(message)

        if guesses not in {"X", "1", "2", "6"}:
            # no need to process anything after this
            return

        guild_db = self.guilds.get_guild(guild_id)
        x_emoji = guild_db.wordle_x_emoji
        two_emoji = guild_db.wordle_two_emoji
        six_emoji = guild_db.wordle_six_emoji

        x_emoji = "😞" if not x_emoji else PartialEmoji.from_str(x_emoji)
        two_emoji = "🎉" if not two_emoji else PartialEmoji.from_str(two_emoji)
        six_emoji = "😬" if not six_emoji else PartialEmoji.from_str(six_emoji)

        if guesses == "X":
            _emoji = x_emoji
        elif guesses in {"1", "2"}:
            _emoji = two_emoji
        elif guesses == "6":
            _emoji = six_emoji

        await message.add_reaction(_emoji)

        await self._handle_tough_day_status(message)
