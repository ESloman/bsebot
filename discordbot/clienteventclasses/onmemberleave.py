
import discord

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.bot_enums import ActivityTypes


class OnMemberLeave(BaseEvent):
    """
    Class for handling when a member leaves the server
    """
    def __init__(self, client, guild_ids, logger):
        super().__init__(client, guild_ids, logger)

    def on_leave(self, member: discord.Member) -> None:
        """
        Method for handling when a member leaves the server.
        We basically just make sure that the user entry is set to inactive
        :param member:
        :return: None
        """
        user_id = member.id

        self.user_points.update({"uid": user_id, "guild_id": member.guild.id}, {"$set": {"inactive": True}})
        self.activities.add_activity(
            user_id,
            member.guild.id,
            ActivityTypes.SERVER_LEAVE
        )
        self.logger.info(f"Deactivating BSEddies account for user - {user_id} - {member.display_name}")
        return
