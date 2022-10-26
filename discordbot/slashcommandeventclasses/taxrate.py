
import discord

import discordbot.views as views
from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies

from mongo.bsedataclasses import TaxRate


class BSEddiesTaxRate(BSEddies):

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.tax_rate = TaxRate()

    async def create_tax_view(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_SET_TAX_RATE, user_id=ctx.user.id
        )

        guild_id = ctx.guild.id
        king_user = self.user_points.get_current_king(guild_id)

        if ctx.user.id != king_user["uid"]:
            message = "You are not the King - you cannot set the tax rate."
            await ctx.respond(content=message, ephemeral=True)
            return

        value = self.tax_rate.get_tax_rate()
        view = views.TaxRateView(value)

        await ctx.respond(view=view, ephemeral=True)
