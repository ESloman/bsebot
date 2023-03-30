
import logging

import discord

from discordbot.bsebot import BSEBot
from discordbot.contextcommands.base import BaseContextCommand


class ContextDeleteMessage(BaseContextCommand):
    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger):
        super().__init__(client, guild_ids, logger)

    async def message_delete(self, ctx: discord.ApplicationContext, message: discord.Message):

        if not self._check_perms(ctx):
            return await self._send_no_perms_message(ctx)

        self.logger.info(f"{ctx.user.name} deleted {message.id}")
        _reason = f"{ctx.user.id}: {ctx.user.name} requested this message be deleted"
        await message.delete(reason=_reason)
        await ctx.respond(content="Message deleted", ephemeral=True)
