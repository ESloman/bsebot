
import discord


class WrappedView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.shared = False

    @discord.ui.button(label="Share", style=discord.ButtonStyle.green)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.shared:
            return
        await interaction.channel.send(content=interaction.message.content)
        self.shared = True
        try:
            await interaction.response.edit_message(content=interaction.message.content, view=None)
        except Exception:
            await interaction.response.defer(ephemeral=True)
