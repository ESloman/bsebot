"""Wrapped view."""

import discord

from discordbot.views.bseview import BSEView


class WrappedView(BSEView):
    """Class for wrapped view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=None)
        self.shared = False

    @discord.ui.button(label="Share", style=discord.ButtonStyle.green)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        if self.shared:
            return
        await interaction.channel.send(content=interaction.message.content)
        self.shared = True
        try:
            await interaction.response.edit_message(content=interaction.message.content, view=None)
        except Exception:
            await interaction.response.defer(ephemeral=True)
