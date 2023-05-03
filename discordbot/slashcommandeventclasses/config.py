
import discord
from logging import Logger

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.config import ConfigView


class Config(BSEddies):
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
        self.dmable = True
        self.activity_type = ActivityTypes.CONFIG
        self.help_string = "Configure BSEBot settings for the user/server"
        self.command_name = "config"

    async def root_config(self, ctx: discord.ApplicationContext) -> None:

        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.CONFIG)

        config_view = ConfigView(self.logger, ctx.user.id, ctx.guild_id)
        msg = (
            "**BSEBot Configuration**\n\n"
            "What would you like to configure?"
        )
        await ctx.respond(content=msg, view=config_view, ephemeral=True)
