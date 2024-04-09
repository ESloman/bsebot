"""Highscore slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.highscore import HighScoreBoardView


class HighScore(BSEddies):
    """Class for handling `/bseddies highscore` commands."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client

        """
        super().__init__(client)
        self.activity_type = ActivityTypes.BSEDDIES_HIGHSCORES
        self.help_string = "See everyone's highest eddie count"
        self.command_name = "highscore"

    async def highscore(self, ctx: discord.ApplicationContext) -> None:
        """Basic method for sending the high score board to the channel that it was requested in.

        Args:
            ctx (discord.ApplicationContext): _description_
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_HIGHSCORES)

        await ctx.channel.trigger_typing()

        highscore_view = HighScoreBoardView(self.embed_manager)
        msg = self.embed_manager.get_highscore_embed(ctx.guild, 5, ctx.author.display_name)
        await ctx.respond(content=msg, view=highscore_view)
