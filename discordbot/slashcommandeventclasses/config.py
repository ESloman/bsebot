
import discord
from logging import Logger

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.config import ConfigView


class BSEddiesConfig(BSEddies):
    """
    Class for handling `/view` commands
    """

    def __init__(
            self,
            client: BSEBot,
            guild_ids: list[int],
            logger: Logger
    ):
        super().__init__(client, guild_ids, logger)

    async def root_config(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.CONFIG)

        config_view = ConfigView(self.logger)
        msg = (
            "**BSEBot Configuration**\n\n"
            "What would you like to configure?"
        )
        await ctx.respond(content=msg, view=config_view, ephemeral=True)