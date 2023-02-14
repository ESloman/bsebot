import datetime

import discord

from discordbot.bot_enums import ActivityTypes, SupporterType
from discordbot.selects.pledge import PledgeSelect

from mongo.bsepoints import UserPoints, Guilds


class PledgeView(discord.ui.View):
    def __init__(self, current=None):
        super().__init__(timeout=None)
        if current is None:
            current = 0

        self.pledge_select = PledgeSelect(current=current)
        self.add_item(self.pledge_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()

    def _append_to_history(self, user_id, guild_id, _type: ActivityTypes, **params):

        doc = {
            "type": _type,
            "timestamp": datetime.datetime.now(),
        }
        if params:
            doc["comment"] = f"Command parameters: {', '.join([f'{key}: {params[key]}' for key in params])}"

        doc["value"] = params["value"]
        self.user_points.append_to_activity_history(user_id, guild_id, doc)

    @discord.ui.button(label="Pledge", style=discord.ButtonStyle.blurple, row=2)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        try:
            value = self.pledge_select.values[0]
        except (IndexError, AttributeError):
            value = [o for o in self.pledge_select.options if o.default][0].value

        self._append_to_history(
            interaction.user.id, interaction.guild.id, ActivityTypes.BSEDDIES_ACTUAL_PLEDGE, value=value
        )

        guild_db = self.guilds.get_guild(interaction.guild.id)

        match value:
            case "supporter":
                self.guilds.add_pledger(interaction.guild.id, interaction.user.id)
                role_id = guild_db["supporter_role"]
                supporter_type = SupporterType.SUPPORTER
            case "revolutionary":
                role_id = guild_db["revolutionary_role"]
                supporter_type = SupporterType.REVOLUTIONARY
            case _:
                role_id = None
                supporter_type = SupporterType.NEUTRAL

        if role_id:
            role = interaction.guild.get_role(role_id)
            await interaction.user.add_roles(role)
        else:
            # user selected "neutral"
            # remove them from revo role if applicable
            role = interaction.guild.get_role(guild_db["revolutionary_role"])
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)

        # remove supporter role
        if value in ["revolutionary", "neutral"]:
            supporter_role = interaction.guild.get_role(guild_db["supporter_role"])
            if supporter_role in interaction.user.roles:
                await interaction.user.remove_roles(supporter_role)
        elif value == "supporter":
            revolutionary_role = interaction.guild.get_role(guild_db["revolutionary_role"])
            if revolutionary_role in interaction.user.roles:
                await interaction.user.remove_roles(revolutionary_role)

        self.user_points.update(
            {"guild_id": interaction.guild.id, "uid": interaction.user.id},
            {"$set": {"supporter_type": supporter_type}}
        )

        await interaction.response.edit_message(
            content=f"Successfully pledged to be **{value}**.", view=None
        )

        if value in ["neutral", "revolutionary"]:
            return

        if not guild_db.get("channel"):
            return

        channel = interaction.guild.get_channel(guild_db["channel"])
        msg = (
            f"{interaction.user.mention} has pledged to support the KING "
            f"and become a <@&{guild_db['supporter_role']}>"
        )
        await channel.send(content=msg, silent=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
