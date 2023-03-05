
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

    async def rename(
        self,
        ctx: discord.ApplicationContext,
        name: str,
        role: str
    ) -> None:
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

        db_guild = self.guilds.get_guild(ctx.guild.id)

        if not db_guild:
            # no guild info in DB ??
            return

        match role:  # noqa
            case "king":
                role_id = db_guild["role"]
                spend = 500
            case "supporter":
                role_id = db_guild["supporter_role"]
                spend = 250
            case "revolutionary":
                role_id = db_guild["revolutionary_role"]
                spend = 250

        if points < spend:
            # too little points
            message = (
                "Sadly, you don't have enough eddies to change this role."
                f" You need **{spend}** to change the {role.upper()} role."
            )
            await ctx.followup.send(content=message, ephemeral=True)
            return

        key = f"rename_{role}"
        last_king_rename = db_guild.get(key)
        now = datetime.datetime.now()
        if last_king_rename:
            time_elapsed = now - last_king_rename
            if time_elapsed.total_seconds() < 3600:
                # not been an hour yet
                mins = round((3600 - time_elapsed.total_seconds()) / 60, 1)
                message = (
                    f"The {role.upper()} role was renamed within the last hour can't be changed again - "
                    f"need to wait another `{mins}` minutes."
                )
                await ctx.followup.send(content=message, ephemeral=True)
                return

        if not role_id:
            await ctx.followup.send("Guild role not set correctly.", ephemeral=True)
            return
        role_obj = ctx.guild.get_role(role_id)

        try:
            await role_obj.edit(name=name)
        except discord.Forbidden:
            message = "Don't have the required permissions to do this."
            await ctx.followup.send(message, ephemeral=True)
            return

        self.user_points.increment_points(
            ctx.author.id,
            ctx.guild.id,
            spend * -1,
            TransactionTypes.KING_RENAME,
            comment=f"Change {role_id} to {name}",
            role_id=role_id
        )

        self.guilds.update({"guild_id": ctx.guild.id}, {"$set": {key: now}})

        channel_id = db_guild.get("channel")
        if channel_id:
            channel = await self.client.fetch_channel(channel_id)
            await channel.trigger_typing()

            # get king user
            king_id = db_guild["king"]
            if role == "king":
                _insert = f"<@{king_id}>"
            else:
                _insert = f"{role.capitalize()}"
            ann = (f"{ctx.author.mention} changed the `bseddies` {role.upper()} role "
                   f"name to **{name}**. {_insert} is now {role_obj.mention}!")
            await channel.send(content=ann)

        message = f"Changed the role name to `{name}` for you."
        await ctx.followup.send(content=message, ephemeral=True)
