"""Leaderboard views."""

import discord

from discordbot.embedmanager import EmbedManager
from discordbot.views.bseview import BSEView


class LeaderBoardView(BSEView):
    """Class for leaderboard view."""

    def __init__(self, embed_manager: EmbedManager) -> None:
        """Initialisation method.

        Args:
            embed_manager (EmbedManager): the embed manager
        """
        self.embeds = embed_manager
        super().__init__(timeout=None)

    @discord.ui.button(label="Expand", style=discord.ButtonStyle.primary, custom_id="leaderboard_button", emoji="📄")
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            button (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        msg = self.embeds.get_leaderboard_embed(
            interaction.guild,
            None if button.label == "Expand" else 5,
            interaction.user.display_name,
        )

        button.label = "Expand" if button.label == "Retract" else "Retract"
        await interaction.response.edit_message(view=self, content=msg)
