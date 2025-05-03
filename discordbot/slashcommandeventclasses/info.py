"""View slash command."""

import discord

from discordbot import __version__
from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class Info(BSEddies):
    """Class for handling `/info` commands."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)
        self.dmable = True
        self.activity_type = ActivityTypes.INFO
        self.help_string = "Retrieves some bot information."
        self.command_name = "info"

    async def info(self, ctx: discord.ApplicationContext) -> None:  # noqa: PLR6301
        """Basic info method for displaying information about the bot.

        Args:
            ctx (discord.ApplicationContext): the command context
        """
        message = f"# BSEBot Information\n\nVersion: `{__version__}`\n[Repo link](https://github.com/ESloman/bsebot)."
        await ctx.respond(content=message, ephemeral=True)
