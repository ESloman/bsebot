"""Contains our ContextDeleteMessage class."""

import discord

from discordbot.bsebot import BSEBot
from discordbot.contextcommands.base import BaseContextCommand


class ContextDeleteMessage(BaseContextCommand):
    """Context class for delete message."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """

    async def message_delete(self, ctx: discord.ApplicationContext, message: discord.Message) -> None:
        """Allows someone to delete a message with a right-click.

        Args:
            ctx (discord.ApplicationContext): application context
            message (discord.Message): the right-clicked message

        Returns:
            None
        """
        if not self._check_perms(ctx):
            return await self._send_no_perms_message(ctx)

        self.logger.info("%s deleted %s", ctx.user.name, message.id)
        _reason = f"{ctx.user.id}: {ctx.user.name} requested this message be deleted"
        await message.delete(reason=_reason)
        await ctx.respond(content="Message deleted", ephemeral=True, delete_after=10)
        return None
