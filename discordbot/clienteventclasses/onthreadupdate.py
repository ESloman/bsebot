
import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent

from mongo.bsedataclasses import SpoilerThreads


class OnThreadUpdate(BaseEvent):
    """
    Class for handling on_thread_update event
    """

    def __init__(self, client: BSEBot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.spoiler_threads = SpoilerThreads()

    async def on_update(self, before: discord.Thread, after: discord.Thread) -> None:
        """
        :param before:
        :param after:
        :return:
        """
        self.logger.info(f"Thread {after.name} has been updated - checking to see if it needs joining")
        thread_members = await after.fetch_members()
        member_ids = [member.id for member in thread_members]
        if self.client.user.id not in member_ids:
            await after.join()
            self.logger.info(f"Joined {after.name}")

        if not self.spoiler_threads.get_thread_by_id(after.guild.id, after.id):
            self.spoiler_threads.insert_spoiler_thread(
                after.guild.id,
                after.id,
                after.name,
                after.created_at,
                after.owner_id,
            )
