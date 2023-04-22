
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.bless import BlessView


class Bless(BSEddies):

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def create_bless_view(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(
            ctx.user, ctx.guild_id, ActivityTypes.BLESS, user_id=ctx.user.id
        )

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db["king"]

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
