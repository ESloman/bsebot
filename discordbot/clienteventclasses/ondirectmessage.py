"""Contains our OnDirectMessage class.

Handles on_direct_message events.
"""

import discord

from apis.giphyapi import GiphyAPI
from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnDirectMessage(BaseEvent):
    """Class for handling on_message events from Discord."""

    def __init__(
        self,
        client: BSEBot,
    ) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self.giphyapi = GiphyAPI()

        self.thanks = ["thank you", "thanks", "fanks", "fank you", " ty ", "thanks dad"]
        self.rude = ["fuck you", "fuck off", "faggot", "fuckyou"]

    async def dm_received(self, message: discord.Message) -> None:
        """Main method for handling when someone sends us a DM.

        Basically, send a random gif if they say 'thank you'

        Args:
            message (discord.Message): the message received
        """
        message_content = message.content

        if [a for a in self.thanks if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("youre welcome")
            await message.author.send(content=gif)
        elif [a for a in self.rude if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("shocked")
            await message.author.send(content=gif)
