
import discord

from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnDirectMessage(BaseEvent):
    """
    Class for handling on_message events from Discord
    """

    def __init__(self, client, guild_ids, logger, giphyapi):
        super().__init__(client, guild_ids, logger)
        self.giphyapi = giphyapi

        self.thanks = ["thank you", "thanks", "fanks", "fank you", " ty ", "thanks dad"]
        self.rude = ["fuck you", "fuck off", "faggot", "fuckyou"]

    async def dm_received(self, message: discord.Message) -> None:
        """
        Main method for handling when someone sends us a DM
        Basically, send a random gif if they say 'thank you'
        :param message:
        :return:
        """
        message_content = message.content

        if [a for a in self.thanks if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("youre welcome")
            await message.author.send(content=gif)
        elif [a for a in self.rude if a in message_content.lower()]:
            gif = await self.giphyapi.random_gif("shocked")
            await message.author.send(content=gif)
