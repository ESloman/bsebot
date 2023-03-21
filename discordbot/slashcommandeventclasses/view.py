
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class BSEddiesView(BSEddies):
    """
    Class for handling `/view` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def view(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling view slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_VIEW)

        ret = self.user_points.find_user(
            ctx.author.id, ctx.guild.id, projection={"points": True, "high_score": True})

        pending = self.user_bets.get_user_pending_points(ctx.author.id, ctx.guild.id)
        msg = (f"You have **{ret['points']}** :money_with_wings:`BSEDDIES`:money_with_wings:!"
               f"\nAdditionally, you have `{pending}` points on 'pending bets'.\n\n"
               f"The _absolute highest_ amount of eddies you've ever had was `{ret.get('high_score', 0)}`!.")
        await ctx.respond(content=msg, ephemeral=True)
