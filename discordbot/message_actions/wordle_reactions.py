
import datetime
import re
from logging import Logger

import discord
from discord import PartialEmoji
from pymongo.errors import OperationFailure

from discordbot import utilities
from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID, SLOMAN_SERVER_ID, WORDLE_SCORE_REGEX
from discordbot.message_actions.base import BaseMessageAction


class WordleMessageAction(BaseMessageAction):
    """
    Wordle message action class for adding reactions to wordle messages
    """
    def __init__(self, client: BSEBot, logger: Logger) -> None:
        super().__init__(client, logger)

    async def pre_condition(self, message: discord.Message, message_type: list) -> bool:
        """
        Wordle precondition. Checks that we're a wordle message using the precalc message_type

        Args:
            message (discord.Message): message to check
            message_type (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        return "wordle" in message_type

    async def run(self, message: discord.Message) -> None:
        """Wordle react/reply action
        Adds a reaction or reply

        Args:
            message (discord.Message): the message to action
        """
        guild_id = message.guild.id
        content = message.content
        result = re.search(WORDLE_SCORE_REGEX, content).group()
        guesses = result.split("/")[0]

        if "🟨" not in content:
            # only greens
            await message.add_reaction("🟩")
        elif content.count("🟨") > content.count("🟩"):
            await message.add_reaction("🟨")

        if guesses not in ["X", "2", "6"]:
            # no need to process anything after this
            return

        # TODO: #307 we should get the emojis from the guild configuration
        if guild_id == BSE_SERVER_ID:
            x_emoji = PartialEmoji.from_str("<:rey:883225332684038154>")
            two_emoji = PartialEmoji.from_str("<a:pookpog:847380557469450281>")
            six_emoji = PartialEmoji.from_str("<:grimace:883385299428855868>")
        elif guild_id == SLOMAN_SERVER_ID:
            x_emoji = PartialEmoji.from_str("<:col:810442635650138132>")
            two_emoji = PartialEmoji.from_str("<a:8194pepeyay:1065934308981887057>")
            six_emoji = PartialEmoji.from_str("<a:8194pepeyay:1065934308981887057>")
        else:
            # not sure on the guild - use a unicode emoji
            x_emoji = "😞"
            two_emoji = "🎉"
            six_emoji = "😬"

        if guesses == "X":
            _emoji = x_emoji
        elif guesses == "2":
            _emoji = two_emoji
        elif guesses == "6":
            _emoji = six_emoji

        await message.add_reaction(_emoji)

        now = datetime.datetime.now()
        today = now.replace(hour=0, minute=0, second=0)

        if not utilities.is_utc(today):
            today = utilities.add_utc_offset(today)

        # get number of 6/6 wordles today
        try:
            wordle_results = self.user_interactions.query(
                {
                    "guild_id": message.guild.id,
                    "is_bot": False,
                    "$text": {"$search": "Wordle 6/6"},
                    "timestamp": {"$gte": today},
                    "message_type": "wordle"
                }
            )
            wordle_results = [r for r in wordle_results if "6/6" in r["content"]]
        except OperationFailure:
            # text index not set correctly
            return

        if len(wordle_results) > 3:

            # make sure we haven't sent this today already
            try:
                link_results = self.user_interactions.query(
                    {
                        "guild_id": message.guild.id,
                        "is_bot": True,
                        "$text": {"$search": "https://imgur.com/Uk73HPD"},
                        "timestamp": {"$gte": today},
                        "message_type": "link"
                    }
                )
                link_results = [r for r in link_results if r["content"] == "https://imgur.com/Uk73HPD"]
            except OperationFailure:
                # text index not set correctly
                return

            if len(link_results) > 0:
                self.logger.info("already sent wordle tough image link")
                return

            await message.channel.send(content="https://imgur.com/Uk73HPD", silent=True)
