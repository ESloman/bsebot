
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.leaderboard import LeaderBoardView


class Leaderboard(BSEddies):
    """
    Class for handling `/leaderboard` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.activity_type = ActivityTypes.BSEDDIES_LEADERBOARD
        self.command_name = "leaderboard"
        self.help_string = "See the BSEddies leaderboard"

    async def leaderboard(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic method for sending the leaderboard to the channel that it was requested in.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, self.activity_type)

        await ctx.channel.trigger_typing()

        leaderboard_view = LeaderBoardView(self.embed_manager)
        msg = self.embed_manager.get_leaderboard_embed(ctx.guild, 5, ctx.author.display_name)
        await ctx.respond(content=msg, view=leaderboard_view)
