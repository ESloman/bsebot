
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
        king_id = guild_db["king"]

        if ctx.user.id != king_id:
            message = "You are not the King - you cannot set the tax rate."
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        value, supporter_value = self.guilds.get_tax_rate(guild_id)
        view = TaxRateView(value, supporter_value)

        msg = f"Please select a tax rate for the peasants and a tax rate for your <@&{guild_db['supporter_role']}>."

        await ctx.respond(content=msg, view=view, ephemeral=True)
