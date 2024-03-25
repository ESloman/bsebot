"""Contains our BaseContextCommand class."""

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent
from discordbot.constants import CREATOR


class BaseContextCommand(BaseEvent):
    """Base Context Command class."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            logger (logging.Logger): the logger
        """
        super().__init__(client)

    def _check_perms(self, ctx: discord.ApplicationContext) -> bool:
        """Checks if the user has the right perms.

        Args:
            ctx (discord.ApplicationContext): the context

        Returns:
            bool: whether they do or don't
        """
        # check if there's a guild
        if not ctx.guild:
            # no-one cares in DMs
            return True

        # is user the creator
        if ctx.user.id == CREATOR:
            return True

        # now we check server perms
        guild_db = self.guilds.get_guild(ctx.guild_id)

        # is user the server owner
        if ctx.user.id == guild_db.owner_id:
            return True

        # is user in server admins
        return ctx.user.id in guild_db.admins

    @staticmethod
    async def _send_no_perms_message(ctx: discord.ApplicationContext) -> None:
        """Sends a message stating they don't have perm.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        msg = "You do not have the required permissions to configure this option."
        await ctx.respond(content=msg, ephemeral=True)
