from typing import Union

import discord

from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import CREATOR


class BSEddies(BaseEvent):
    """
    A base BSEddies event for any shared methods across
    All slash command classes will inherit from this class
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def _handle_validation(self, ctx: Union[discord.ApplicationContext, discord.Interaction], **kwargs) -> bool:
        """
        Internal method for validating slash command inputs.
        :param ctx: discord ctx to use
        :param kwargs: the additional kwargs to use in validation
        :return: True or False
        """
        if kwargs.get("admin") and ctx.author.id != CREATOR:
            msg = "You do not have the permissions to use this command."
            await ctx.respond(content=msg, ephemeral=True)
            return False

        if "friend" in kwargs and (
                isinstance(kwargs["friend"], discord.User) or isinstance(kwargs["friend"], discord.Member)):
            if kwargs["friend"].bot:
                msg = "Bots cannot be gifted eddies."
                await ctx.respond(content=msg, ephemeral=True)
                return False

            if kwargs["friend"].id == ctx.author.id:
                msg = "You can't gift yourself points."
                await ctx.respond(content=msg, ephemeral=True)
                return False

        if "amount" in kwargs and isinstance(kwargs["amount"], int):
            if kwargs["amount"] < 0:
                msg = "You can't _\"gift\"_ someone negative points."
                await ctx.respond(content=msg, ephemeral=True)
                return False

        return True
