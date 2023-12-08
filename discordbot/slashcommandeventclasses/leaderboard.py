"""Leaderboard slash command."""

import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.leaderboard import LeaderBoardView


class Leaderboard(BSEddies):
    """Class for handling `/leaderboard` commands."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.activity_type = ActivityTypes.BSEDDIES_LEADERBOARD
        self.command_name = "leaderboard"
        self.help_string = "See the BSEddies leaderboard"

    async def leaderboard(self, ctx: discord.ApplicationContext) -> None:
        """Basic method for sending the leaderboard to the channel that it was requested in.

        Args:
            ctx (discord.ApplicationContext): the context
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, self.activity_type)

        await ctx.channel.trigger_typing()

        leaderboard_view = LeaderBoardView(self.embed_manager)
        msg = self.embed_manager.get_leaderboard_embed(ctx.guild, 5, ctx.author.display_name)
        await ctx.respond(content=msg, view=leaderboard_view)
