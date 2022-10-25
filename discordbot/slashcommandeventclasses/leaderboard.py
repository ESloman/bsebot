
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies
from discordbot.views import LeaderBoardView


class BSEddiesLeaderboard(BSEddies):
    """
    Class for handling `/leaderboard` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def leaderboard(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic method for sending the leaderboard to the channel that it was requested in.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_LEADERBOARD)

        leaderboard_view = LeaderBoardView(self.embed_manager)
        msg = self.embed_manager.get_leaderboard_embed(ctx.guild, 5)
        await ctx.respond(content=msg, view=leaderboard_view)