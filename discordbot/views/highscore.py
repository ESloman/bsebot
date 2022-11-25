
import discord
from discordbot.embedmanager import EmbedManager


class HighScoreBoardView(discord.ui.View):
    def __init__(self, embed_manager: EmbedManager):
        self.embeds = embed_manager
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Expand",
        style=discord.ButtonStyle.primary,
        custom_id="highscore_button",
        emoji="📄"
        )
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """
        Button Callback
        :param button:
        :param interaction:
        :return:
        """
        msg = self.embeds.get_highscore_embed(
            interaction.guild,
            None if button.label == "Expand" else 5,
            interaction.user.display_name
        )

        button.label = "Expand" if button.label == "Retract" else "Retract"
        await interaction.response.edit_message(view=self, content=msg)
