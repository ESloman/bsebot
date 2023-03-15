import discord
from discordbot.selects.config import ConfigSelect


class ConfigView(discord.ui.View):
    def __init__(
        self,
    ):
        super().__init__(timeout=120)
        self.config_select = ConfigSelect()
        self.add_item(self.config_select)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Thanks", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.edit_original_message(content="Cancelled.")
        await interaction.response.send_message("Thanks", ephemeral=True)
