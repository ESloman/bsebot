
import discord

from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnReadyEvent(BaseEvent):
    """
    Class for handling on_ready event
    """
    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.finished = False

    async def on_ready(self) -> None:
        """
        Method called for on_ready event.
        """
        self.logger.info("Beginning OnReady sequence")
        self.logger.info(f"Connected as {self.client.user.name}")
        self.logger.info("Finished OnReady sequence")
        self.finished = True
