
import logging

import discord

from discordbot.bsebot import BSEBot
from discordbot.contextcommands.base import BaseContextCommand
from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.views.usergift import GiftUserEddiesView


class ContextUserGift(BaseContextCommand):
    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger, gift: Gift):
        super().__init__(client, guild_ids, logger)
        self.gift = gift

    async def user_gift(self, ctx: discord.ApplicationContext, user: discord.Member):

        our_user = self.user_points.find_user(ctx.user.id, ctx.guild.id)
        eddies = our_user.points
        view = GiftUserEddiesView(eddies, user, self.gift)

        await ctx.respond(view=view, ephemeral=True)
