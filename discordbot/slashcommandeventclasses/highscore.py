
import discord

import discordbot.views as views
from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies


class BSEddiesHighScore(BSEddies):
    """
    Class for handling `/bseddies highscore` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def highscore(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic method for sending the high score board to the channel that it was requested in.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_HIGHSCORES)

        highscore_view = views.HighScoreBoardView(self.embed_manager)
        msg = self.embed_manager.get_highscore_embed(ctx.guild, 5)
        await ctx.respond(content=msg, view=highscore_view)
