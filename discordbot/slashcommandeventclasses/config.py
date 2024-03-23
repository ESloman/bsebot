"""Config slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.config import ConfigView


class Config(BSEddies):
    """Class for handling `/view` commands."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs

        """
        super().__init__(client, guild_ids)
        self.dmable = True
        self.activity_type = ActivityTypes.CONFIG
        self.help_string = "Configure BSEBot settings for the user/server"
        self.command_name = "config"

    async def root_config(self, ctx: discord.ApplicationContext) -> None:
        """Root config.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.CONFIG)

        config_view = ConfigView(self.logger, ctx.user.id, ctx.guild_id)
        msg = "## BSEBot Configuration\n\nWhat would you like to configure?"
        await ctx.respond(content=msg, view=config_view, ephemeral=True)
