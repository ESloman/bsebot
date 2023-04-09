import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.pledge import PledgeView


class BSEddiesPledge(BSEddies):

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def create_pledge_view(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_PLEDGE, user_id=ctx.user.id
        )

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db["king"]

        if ctx.user.id == king_id:
            message = "You are not the King - you cannot pledge."
            await ctx.respond(content=message, ephemeral=True)
            return

        if ctx.user.id in guild_db.get("pledged", []):
            # can't pledge again when they've already pledged support
            message = "You're already locked in to support the King this week."
            await ctx.respond(content=message, ephemeral=True)
            return

        user_db = self.user_points.find_user(ctx.user.id, guild_id)
        current = user_db.get("supporter_type", 0)

        view = PledgeView(current)

        msg = (
            "Pledge to be a supporter or a revolutionary. "
            "Once a supporter; you are locked in until after the next revolution (or until the King changes). "
            "You will automatically _'support'_ the KING at the next revolution."
        )

        await ctx.respond(content=msg, view=view, ephemeral=True)
