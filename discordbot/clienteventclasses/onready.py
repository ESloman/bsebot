"""Contains our OnReadyEvent class.

Handles on_ready events.
"""

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnReadyEvent(BaseEvent):
    """Class for handling on_ready event."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self.finished = False

    async def on_ready(self) -> None:
        """Method called for on_ready event."""
        self.logger.info("Beginning OnReady sequence")
        self.logger.info("Connected as %s", self.client.user.name)
        self.logger.info("Finished OnReady sequence")
        self.finished = True
