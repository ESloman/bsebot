"""Revolution config views."""

import discord

from discordbot.selects.revolutionconfig import RevolutionEnableSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class RevolutionConfigView(BSEView):
    """Class for revolution config view."""

    def __init__(self, enabled: bool = True) -> None:
        """Initialisation method.

        Args:
            enabled (bool, optional): whether we're currently enabled or not. Defaults to True.
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.user_points = UserPoints()

        self.enabled_select = RevolutionEnableSelect(enabled)
        self.add_item(self.enabled_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        enabled = self.get_select_value(self.enabled_select)
        enabled_bool = enabled == "enabled"

        self.guilds.set_revolution_toggle(interaction.guild_id, enabled_bool)

        await interaction.response.edit_message(content=f"Revolution event {enabled}", view=None, delete_after=10)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
