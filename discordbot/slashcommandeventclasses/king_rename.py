
import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSEDDIES_KING_ROLES
from discordbot.slashcommandeventclasses import BSEddies


class BSEddiesKingRename(BSEddies):
    """
    Class for handling `/renameking` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def rename(self, ctx: discord.ApplicationContext, name: str) -> None:
        """
        Method for a user to rename the BSEddies KING role for small cost.
        The role can't be changed more than once an hour.

        :param ctx:
        :param name:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.RENAME_KING)

        ret = self.user_points.find_user(ctx.author.id, ctx.guild.id, projection={"points": True})
        points = ret["points"]

        if points < 500:
            # too little points
            message = "Sadly, you don't have enough eddies to change the King's role. You need **500**"
            await ctx.followup.send(content=message, ephemeral=True)
            return

        db_guild = self.guilds.get_guild(ctx.guild.id)
        last_king_rename = db_guild.get("rename_king")
        now = datetime.datetime.now()
        if last_king_rename:
            time_elapsed = now - last_king_rename
            if time_elapsed.total_seconds() < 3600:
                # not been an hour yet
                message = (
                    "The KING role was renamed within the last hour can't be changed again - "
                    f"need to wait another {3600 - time_elapsed.total_seconds()} seconds."
                )
                await ctx.followup.send(content=message, ephemeral=True)
                return

        role = ctx.guild.get_role(BSEDDIES_KING_ROLES[ctx.guild.id])

        self.user_points.decrement_points(ctx.author.id, ctx.guild.id, 500)

        await role.edit(name=name)

        self.guilds.update({"guild_id": ctx.guild.id}, {"$set": {"rename_king": now}})

        message = f"Changed the role name to `{name}` for you."
        await ctx.followup.send(content=message, ephemeral=True)
