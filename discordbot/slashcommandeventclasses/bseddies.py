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
        self.dmable = False

    async def _handle_validation(self, ctx: Union[discord.ApplicationContext, discord.Interaction], **kwargs) -> bool:
        """
        Internal method for validating slash command inputs.
        :param ctx: discord ctx to use
        :param kwargs: the additional kwargs to use in validation
        :return: True or False
        """

        if type(ctx) == discord.ApplicationContext:
            response = ctx.respond
        else:
            response = ctx.response.send_message

        if not ctx.guild and not self.dmable:
            msg = "This command doesn't work in DMs (yet)."
            await response(content=msg)
            return False

        if kwargs.get("admin") and ctx.user.id != CREATOR:
            msg = "You do not have the permissions to use this command."
            await response(content=msg, ephemeral=True, delete_after=10)
            return False

        if "friend" in kwargs and (
                isinstance(kwargs["friend"], discord.User) or isinstance(kwargs["friend"], discord.Member)):
            if kwargs["friend"].bot:
                msg = "Bots cannot be gifted eddies."
                await response(content=msg, ephemeral=True, delete_after=10)
                return False

            if kwargs["friend"].id == ctx.user.id:
                msg = "You can't gift yourself points."
                await response(content=msg, ephemeral=True, delete_after=10)
                return False

        if "amount" in kwargs and isinstance(kwargs["amount"], int):
            if kwargs["amount"] < 0:
                msg = "You can't _\"gift\"_ someone negative points."
                await response(content=msg, ephemeral=True, delete_after=10)
                return False

        return True
