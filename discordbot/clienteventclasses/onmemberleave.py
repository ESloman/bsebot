"""Contains our OnMemberLeave class.

Handles on_member_leave events.
"""

import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnMemberLeave(BaseEvent):
    """Class for handling when a member leaves the server."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)

    def on_leave(self, member: discord.Member) -> None:
        """Method for handling when a member leaves the server.

        We basically just make sure that the user entry is set to inactive

        Args:
            member (discord.Member): the member that joined
        """
        user_id = member.id

        self.user_points.update({"uid": user_id, "guild_id": member.guild.id}, {"$set": {"inactive": True}})
        self.activities.add_activity(user_id, member.guild.id, ActivityTypes.SERVER_LEAVE)
        self.logger.info("Deactivating BSEddies account for user - %s - %s", user_id, member.display_name)
