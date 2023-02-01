
import datetime

import discord

from discordbot.bot_enums import ActivityTypes, TransactionTypes
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

        if not db_guild:
            # no guild info in DB ??
            return

        last_king_rename = db_guild.get("rename_king")
        now = datetime.datetime.now()
        if last_king_rename:
            time_elapsed = now - last_king_rename
            if time_elapsed.total_seconds() < 3600:
                # not been an hour yet
                mins = round((3600 - time_elapsed.total_seconds()) / 60, 1)
                message = (
                    "The KING role was renamed within the last hour can't be changed again - "
                    f"need to wait another `{mins}` minutes."
                )
                await ctx.followup.send(content=message, ephemeral=True)
                return

        role_id = db_guild.get("role")

        if not role_id:
            await ctx.followup.send("Guild role not set correctly.", ephemeral=True)
            return
        role = ctx.guild.get_role(role_id)

        try:
            await role.edit(name=name)
        except discord.Forbidden:
            message = "Don't have the required permissions to do this."
            await ctx.followup.send(message, ephemeral=True)
            return

        self.user_points.decrement_points(ctx.author.id, ctx.guild.id, 500)

        self.user_points.append_to_transaction_history(
            ctx.author.id,
            ctx.guild.id,
            {
                "type": TransactionTypes.GIFT_GIVE,
                "amount": 500 * -1,
                "timestamp": datetime.datetime.now(),
                "role_id": role_id,
                "guild_id": ctx.guild.id
            }
        )

        self.guilds.update({"guild_id": ctx.guild.id}, {"$set": {"rename_king": now}})

        channel_id = db_guild.get("channel")
        if channel_id:
            channel = await ctx.guild.fetch_channel(channel_id)
            await channel.trigger_typing()

            # get king user
            king_user = self.user_points.get_current_king(ctx.guild.id)
            user_id = king_user["uid"]
            ann = (f"{ctx.author.mention} changed the `bseddies` KING role "
                   f"name to **{name}**. <@{user_id}> is now {role.mention}!")
            await channel.send(content=ann)

        message = f"Changed the role name to `{name}` for you."
        await ctx.followup.send(content=message, ephemeral=True)
