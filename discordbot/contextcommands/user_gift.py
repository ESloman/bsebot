"""Contains our ContextUserGift class."""

import logging

import discord

from discordbot.bsebot import BSEBot
from discordbot.contextcommands.base import BaseContextCommand
from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.views.usergift import GiftUserEddiesView


class ContextUserGift(BaseContextCommand):
    """Context class for gifting."""

    def __init__(self, client: BSEBot, guild_ids: list[int], logger: logging.Logger, gift: Gift) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
            gift (Gift): the gift class to use
        """
        super().__init__(client, guild_ids, logger)
        self.gift = gift

    async def user_gift(self, ctx: discord.ApplicationContext, user: discord.Member) -> None:
        """Allows users to gift eddies by right-clicking another user.

        Args:
            ctx (discord.ApplicationContext): the application context
            user (discord.Member): the user right-clicked
        """
        our_user = self.user_points.find_user(ctx.user.id, ctx.guild.id)
        eddies = our_user.points
        view = GiftUserEddiesView(eddies, user, self.gift)

        await ctx.respond(view=view, ephemeral=True)
