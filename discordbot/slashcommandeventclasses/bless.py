"""Bless slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.bless import BlessView


class Bless(BSEddies):
    """Class for Bless command."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client

        """
        super().__init__(client)
        self.activity_type = ActivityTypes.BSEDDIES_ACTIVE
        self.help_string = "Allows the KING to bless supporters/everyone"
        self.command_name = "bless"

    async def create_bless_view(self, ctx: discord.ApplicationContext) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.user, ctx.guild_id, ActivityTypes.BLESS)

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db.king

        if ctx.user.id != king_id:
            message = "You are not the King - you cannot bless."
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        view = BlessView()

        msg = (
            "Please select _who_ to bless and how much by. "
            "Eddies will be distributed equally between selected user group."
        )

        await ctx.respond(content=msg, view=view, ephemeral=True)
