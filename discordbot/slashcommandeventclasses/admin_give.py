"""Admin give slash command."""

import contextlib

import discord

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class AdminGive(BSEddies):
    """Class for handling `/bseddies admin give` command."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs

        """
        super().__init__(client, guild_ids)
        self.activity_type = ActivityTypes.BSEDDIES_ADMIN_GIVE
        self.help_string = "Allows an admin to give a user eddies"
        self.command_name = "admin_give"

    async def admin_give(self, ctx: discord.ApplicationContext, user: discord.User, amount: int) -> None:
        """Command to give a user some extra eddies.

        Args:
            ctx (discord.ApplicationContext): _description_
            user (discord.User): _description_
            amount (int): _description_
        """
        if not await self._handle_validation(ctx, admin=True):
            return

        self._add_event_type_to_activity_history(
            ctx.user,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_ADMIN_GIVE,
            targeted_id=user.id,
            amount=amount,
        )

        self.user_points.increment_points(
            user.id,
            ctx.guild.id,
            amount,
            TransactionTypes.ADMIN_GIVE,
            comment="Admin override increment",
        )

        with contextlib.suppress(discord.Forbidden, discord.ApplicationCommandInvokeError):
            await user.send(content=f"You've been given {amount} eddies by an admin.", silent=True)

        await ctx.respond(content=f"Given {user.display_name} {amount} eddies.", ephemeral=True, delete_after=10)
