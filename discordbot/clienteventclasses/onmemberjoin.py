"""Contains our OnMemberJoin class.

Handles on_member_create events.
"""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnMemberJoin(BaseEvent):
    """Class for handling when a new member joins the server."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
        """
        super().__init__(client, guild_ids)

    def on_join(self, member: discord.Member) -> None:
        """Method for handling when a new member joins the server.

        We basically just make sure that the user has an entry in our DB

        Args:
            member (discord.Member): the member that joined
        """
        user_id = member.id

        self.activities.add_activity(user_id, member.guild.id, ActivityTypes.SERVER_JOIN)

        if user := self.user_points.find_user(user_id, member.guild.id):
            self.user_points.update({"_id": user._id}, {"$set": {"inactive": False}})  # noqa: SLF001
            self.logger.info("Activating BSEddies account for existing user - %s - %s", user_id, member.display_name)
            return

        name = member.nick or member.name
        self.user_points.create_user(user_id, member.guild.id, name)
        self.logger.info("Creating BSEddies account for new user - %s - %s", user_id, member.display_name)
