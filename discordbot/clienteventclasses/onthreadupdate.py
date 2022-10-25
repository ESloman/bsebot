
import discord

from discordbot.baseeventclass import BaseEvent


class OnThreadUpdate(BaseEvent):
    """
    Class for handling on_thread_update event
    """

    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)

    async def on_update(self, before: discord.Thread, after: discord.Thread) -> None:
        """

        :param before:
        :param after:
        :return:
        """

        if before.archived and not after.archived:
            self.logger.info(f"Thread has been unarchived - joining")
            thread_members = await after.fetch_members()
            member_ids = [member.id for member in thread_members]
            if self.client.user.id not in member_ids:
                await after.join()
                self.logger.info(f"Joining unarchived thread")
