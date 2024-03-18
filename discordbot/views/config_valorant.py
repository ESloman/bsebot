"""Valorant config views."""

import discord
from bson import Int64

from discordbot.selects.valorantconfig import ValorantActiveSelect, ValorantChannelSelect, ValorantRoleSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds


class ValorantConfigView(BSEView):
    """Class for valorant config views."""

    def __init__(self, guild_id: int) -> None:
        """Initialisation method.

        Args:
            guild_id (int): the guild ID
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()

        guild_db = self.guilds.get_guild(guild_id)
        active = "1" if guild_db.valorant_rollcall else "0"

        self.active_select = ValorantActiveSelect(active)
        self.channel_select = ValorantChannelSelect()
        self.role_select = ValorantRoleSelect()

        if int(active):
            self.channel_select.disabled = False
            self.role_select.disabled = False

        self.add_item(self.active_select)
        self.add_item(self.channel_select)
        self.add_item(self.role_select)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        active_val = bool(int(self.get_select_value(self.active_select)))
        self.channel_select.disabled = not active_val
        self.role_select.disabled = not active_val

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)

        active_val = bool(int(self.get_select_value(self.active_select)))

        channel = self.get_select_value(self.channel_select) or guild_db.valorant_channel
        channel = int(channel) if channel is not None else guild_db.valorant_channel
        if channel and type(channel) not in {int, Int64}:
            channel = channel.id

        role = self.get_select_value(self.role_select) or guild_db.valorant_role
        role = int(role) if role is not None else guild_db.valorant_role
        if role and type(role) not in {int, Int64}:
            role = role.id

        self.guilds.set_valorant_config(interaction.guild_id, active_val, channel, role)

        await interaction.response.edit_message(content="Valorant config updated.", view=None, delete_after=10)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
