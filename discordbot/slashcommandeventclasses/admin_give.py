
import discord

from discordbot.bot_enums import TransactionTypes, ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class BSEddiesAdminGive(BSEddies):
    """
    Class for handling `/bseddies admin give` command
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def admin_give(self, ctx: discord.ApplicationContext, user: discord.User, amount: int) -> None:
        """
        Command to give a user some extra eddies.
        :param ctx:
        :param user:
        :param amount:
        :return:
        """
        if not await self._handle_validation(ctx, admin=True):
            return

        self._add_event_type_to_activity_history(
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_ADMIN_GIVE, user_id=user.id, amount=amount
        )

        self.user_points.increment_points(
            user.id,
            ctx.guild.id,
            amount,
            TransactionTypes.ADMIN_GIVE,
            comment="Admin override increment"
        )

        try:
            await user.send(content=f"You've been given {amount} eddies by an admin.", silent=True)
        except (discord.Forbidden, discord.ApplicationCommandInvokeError):
            pass

        await ctx.respond(content=f"Given {user.display_name} {amount} eddies.", ephemeral=True)
