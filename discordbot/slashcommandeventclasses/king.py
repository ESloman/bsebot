import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSEDDIES_KING_ROLES
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class BSEddiesKing(BSEddies):
    """
    Class for handling `/king` command
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def king_data(self, ctx: discord.ApplicationContext) -> None:
        """

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_KING)

        guild_id = ctx.guild.id

        king_user = self.user_points.get_current_king(guild_id)
        data = self.user_points.get_king_info(king_user)

        role_id = BSEDDIES_KING_ROLES[guild_id]
        role = ctx.guild.get_role(role_id)
        member = ctx.guild.get_member(king_user["uid"])  # type: discord.Member

        message = (f"**King Info**\n"
                   f"{member.mention} is our current {role.mention}. They've been King for "
                   f"{str(datetime.timedelta(seconds=data['current']))}.\n\n"
                   f"The total amount of time they've spent as KING is "
                   f"`{str(datetime.timedelta(seconds=data['total']))}`\n"
                   f"They've been {role.mention} **{data['times']}** times.\n"
                   f"The longest they've been {role.mention} for is "
                   f"{str(datetime.timedelta(seconds=max(data['all_times'])))}")
        await ctx.respond(content=message)
