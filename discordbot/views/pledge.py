"""Pledge views."""

import discord

from discordbot.bot_enums import ActivityTypes, SupporterType
from discordbot.selects.pledge import PledgeSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class PledgeView(BSEView):
    """Class for pledge view."""

    def __init__(self, current: SupporterType = None) -> None:
        """Initialisation method.

        Args:
            current (SupporterType, optional): the current supporter value. Defaults to None.
        """
        super().__init__(timeout=None)
        if current is None:
            current = 0

        self.pledge_select = PledgeSelect(current=current)
        self.add_item(self.pledge_select)
        self.guilds = Guilds()
        self.activities = UserActivities()
        self.user_points = UserPoints()

    @discord.ui.button(label="Pledge", style=discord.ButtonStyle.blurple, row=2)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        # defer first
        await interaction.response.defer(ephemeral=True)

        value = self.get_select_value(self.pledge_select)

        self.activities.add_activity(
            interaction.user.id,
            interaction.guild.id,
            ActivityTypes.BSEDDIES_ACTUAL_PLEDGE,
            value=value,
        )

        guild_db = self.guilds.get_guild(interaction.guild.id)

        match value:
            case "supporter":
                self.guilds.add_pledger(interaction.guild.id, interaction.user.id)
                role_id = guild_db.supporter_role
                supporter_type = SupporterType.SUPPORTER
            case "revolutionary":
                role_id = guild_db.revolutionary_role
                supporter_type = SupporterType.REVOLUTIONARY
            case _:
                role_id = None
                supporter_type = SupporterType.NEUTRAL

        print(f"{interaction.user.name} selected {value}")

        try:
            if role_id:
                role = interaction.guild.get_role(role_id)
                await interaction.user.add_roles(role)
            else:
                # user selected "neutral"
                # remove them from revo role if applicable
                role = interaction.guild.get_role(guild_db.revolutionary_role)
                if role in interaction.user.roles:
                    await interaction.user.remove_roles(role)
        except Exception as e:
            print(f"Got error adding the new role: {e}")

        # remove supporter role
        try:
            if value in {"revolutionary", "neutral"}:
                supporter_role = interaction.guild.get_role(guild_db.supporter_role)
                if supporter_role in interaction.user.roles:
                    await interaction.user.remove_roles(supporter_role)
            elif value == "supporter":
                revolutionary_role = interaction.guild.get_role(guild_db.revolutionary_role)
                if revolutionary_role in interaction.user.roles:
                    await interaction.user.remove_roles(revolutionary_role)
        except Exception as e:
            print(f"Got error removing the old role: {e}")

        self.user_points.update(
            {"guild_id": interaction.guild.id, "uid": interaction.user.id},
            {"$set": {"supporter_type": supporter_type}},
        )

        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            content=f"Successfully pledged to be **{value}**.",
            view=None,
        )

        if value in {"neutral", "revolutionary"}:
            return

        if not guild_db.channel:
            return

        channel = interaction.guild.get_channel(guild_db.channel)
        msg = f"{interaction.user.mention} has pledged to support the KING and become a <@&{guild_db.supporter_role}>"
        await channel.send(content=msg, silent=True)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
