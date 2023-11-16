"""Contains our OnReadyEvent class.

Handles on_ready events.
"""

import logging

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnReadyEvent(BaseEvent):
    """Class for handling on_ready event."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.finished = False

    async def on_ready(self) -> None:
        """Method called for on_ready event."""
        self.logger.info("Beginning OnReady sequence")
        self.logger.info("Connected as %s", self.client.user.name)
        self.logger.info("Finished OnReady sequence")
        self.finished = True
