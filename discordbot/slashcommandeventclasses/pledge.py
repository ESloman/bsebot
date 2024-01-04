"""Pledge slash command."""

import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.pledge import PledgeView


class Pledge(BSEddies):
    """Class for pledge command."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.activity_type = ActivityTypes.BSEDDIES_PLEDGE
        self.help_string = "Pledge your support to a faction"
        self.command_name = "pledge"

    async def create_pledge_view(self, ctx: discord.ApplicationContext) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_PLEDGE)

        guild_id = ctx.guild.id
        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db.king

        if ctx.user.id == king_id:
            message = "You are not the King - you cannot pledge."
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        if ctx.user.id in guild_db.pledged:
            # can't pledge again when they've already pledged support
            message = "You're already locked in to support the King this week."
            await ctx.respond(content=message, ephemeral=True, delete_after=10)
            return

        user_db = self.user_points.find_user(ctx.user.id, guild_id)
        current = user_db.supporter_type

        view = PledgeView(current)

        msg = (
            "Pledge to be a supporter or a revolutionary. "
            "Once a supporter; you are locked in until after the next revolution (or until the King changes). "
            "You will automatically _'support'_ the KING at the next revolution."
        )

        await ctx.respond(content=msg, view=view, ephemeral=True)
