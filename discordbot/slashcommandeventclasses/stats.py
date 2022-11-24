
import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies
from discordbot.stats.statsbuilder import PersonalStatsBuilder


class BSEddiesStats(BSEddies):
    """
    Class for handling `/view` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.stats_builder = PersonalStatsBuilder(client, logger)

    async def stats(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling view slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.STATS)

        now = datetime.datetime.now()

        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)
        if start.month == 12:
            new_month = 1
        else:
            new_month = start.month + 1
        end = start.replace(month=new_month)

        message = await self.stats_builder.get_stats_message_for_user(
            ctx.guild_id, ctx.author.id, start, end
        )

        await ctx.followup.send(content=message, ephemeral=True)
