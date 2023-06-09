
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.taxrate import TaxRateView


class TaxRate(BSEddies):

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.activity_type = ActivityTypes.BSEDDIES_SET_TAX_RATE
        self.help_string = "Set the tax rate for the server"
        self.command_name = "taxrate"

    async def create_tax_view(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_SET_TAX_RATE
        )

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db.king

        value, supporter_value = self.guilds.get_tax_rate(guild_id)

        message = (
            "Tax rate is currently:\n"
            f"- `{value * 100}%`\n"
            f"- `{supporter_value * 100}%` for supporters"
        )

        if ctx.user.id != king_id:
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        view = TaxRateView(value, supporter_value)

        message += (
            f"\n\nPlease select a general tax rate and a tax rate for your <@&{guild_db.supporter_role}>. "
            "Leave it as is to not change anything at all."
        )
        await ctx.respond(content=message, view=view, ephemeral=True)
