"""Taxrate slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.taxrate import TaxRateView


class TaxRate(BSEddies):
    """Class for taxrate command."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs

        """
        super().__init__(client, guild_ids)
        self.activity_type = ActivityTypes.BSEDDIES_SET_TAX_RATE
        self.help_string = "Set the tax rate for the server"
        self.command_name = "taxrate"

    async def create_tax_view(self, ctx: discord.ApplicationContext) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_SET_TAX_RATE)

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db.king

        value, supporter_value = self.guilds.get_tax_rate(guild_id)

        message = "Tax rate is currently:\n" f"- `{value * 100}%`\n- `{supporter_value * 100}%` for supporters"

        if ctx.user.id != king_id:
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        view = TaxRateView(value, supporter_value)

        message += (
            f"\n\nPlease select a general tax rate and a tax rate for your <@&{guild_db.supporter_role}>. "
            "Leave it as is to not change anything at all."
        )
        await ctx.respond(content=message, view=view, ephemeral=True)
