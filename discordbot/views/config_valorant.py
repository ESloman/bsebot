"""Valorant config views."""

import discord
from bson import Int64

from discordbot.selects.valorantconfig import ValorantActiveSelect, ValorantChannelSelect, ValorantRoleSelect
from mongo.bsepoints.guilds import Guilds


class ValorantConfigView(discord.ui.View):
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
        try:
            active_val = self.active_select.values[0]
        except (IndexError, AttributeError, TypeError):
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        self.channel_select.disabled = not active_val
        self.role_select.disabled = not active_val

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(  # noqa: C901, PLR0912
        self, _: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)

        try:
            active_val = bool(int(self.active_select.values[0]))
        except (IndexError, AttributeError, TypeError):
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        channel = guild_db.valorant_channel
        try:
            channel = self.channel_select.values[0]
        except (AttributeError, IndexError):
            for opt in self.channel_select.options:
                if opt.default:
                    channel = opt.value
                    break

        if channel and type(channel) not in {int, Int64}:
            channel = channel.id

        role = guild_db.valorant_role
        try:
            role = self.role_select.values[0]
        except (AttributeError, IndexError):
            for opt in self.role_select.options:
                if opt.default:
                    role = opt.value
                    break

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
