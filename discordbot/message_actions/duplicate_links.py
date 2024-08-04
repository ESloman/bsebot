"""Duplicate link message class."""

import datetime
import random
import re
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import discord
from pymongo.errors import OperationFailure

from discordbot.bsebot import BSEBot
from discordbot.message_actions.base import BaseMessageAction
from discordbot.message_strings.duplicate_links import MESSAGES

if TYPE_CHECKING:
    from mongo.datatypes.message import MessageDB


class DuplicateLinkAction(BaseMessageAction):
    """Duplicated Link action."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): our BSEBot client
        """
        super().__init__(client)
        # allow the precondition to store results for the run to use
        self._results_map: dict[int, list[MessageDB]] = {}

    async def pre_condition(self, message: discord.Message, message_type: list[str]) -> bool:
        """Duplicated links precondition.

        Args:
            message (discord.Message): message to check
            message_type (list): the precalculated message_type of the message

        Returns:
            bool: true or false
        """
        if "link" not in message_type or message.author.bot:
            return False

        # extract link from content
        try:
            link = next(
                _link
                for _link in re.split(" \n", message.content)
                if "https" in _link and any(x in _link for x in ["twitter", "x.com", "youtube"])
            )
        except StopIteration:
            return False

        if "youtube" not in link:
            link = link.split("?")[0]

        # only care about dupes if the original was posted within a couple of days
        threshold = datetime.datetime.now(tz=ZoneInfo("UTC")) - datetime.timedelta(days=2)
        try:
            results = self.user_interactions.query(
                {
                    "guild_id": message.guild.id,
                    "is_bot": False,  # don't care if the original poster was a bot
                    "message_id": {"$ne": message.id},  # don't trigger off of original message
                    "$text": {"$search": link},
                    "timestamp": {"$gte": threshold},
                },
            )
        except OperationFailure:
            # index not set correctly
            # could be local dev env
            return False

        # text searching can find false positives
        # make sure our exact link is present
        results = [result for result in results if link in result.content]

        if not results:
            return False

        results = sorted(results, key=lambda x: x.timestamp, reverse=False)

        # make sure that our message still exists - could have been deleted
        actual_results: list[MessageDB] = []
        for result in results:
            res_channel = await self.client.fetch_channel(result.channel_id)
            try:
                await res_channel.fetch_message(result.message_id)
            except discord.NotFound:
                continue
            actual_results.append(result)

        self._results_map[message.id] = results
        return True

    async def run(self, message: discord.Message) -> None:
        """Duplicate link action.

        Args:
            message (discord.Message): the message to action
        """
        original = self._results_map[message.id][0]

        # link to the original message
        original_message_link = (
            f"https://discord.com/channels/{message.guild.id}/{original.channel_id}/{original.message_id}"
        )

        msg = random.choice(MESSAGES)
        msg = msg.format(mention=f"<@{original.user_id}>")
        msg += f"\n\n{original_message_link}"

        await message.reply(content=msg, suppress=True)

        # remove results
        self._results_map.pop(message.id)
