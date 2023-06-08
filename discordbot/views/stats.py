
import discord

from discordbot.selects.stats import StatsModeSelect


class StatsView(discord.ui.View):
    def __init__(
        self,
        stats_class  # discordbot.slashcommandeventclasses.stats.Stats - can't import due to circular imports
    ):
        super().__init__(timeout=None)

        self.stats_class = stats_class
        self.stats_mode = StatsModeSelect()

        self.add_item(self.stats_mode)

    async def update(self, interaction: discord.Interaction):

        value = None
        try:
            value = self.stats_mode.values[0]
        except (IndexError, AttributeError):
            for opt in self.stats_mode.options:
                if opt.default:
                    value = opt.value
                    break

        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Submit":
                child.disabled = not bool(value)
                break

        await interaction.response.edit_message(
            content=interaction.message.content,
            view=self
        )

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=False)
    async def submit_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        value = None
        try:
            value = self.stats_mode.values[0]
        except (IndexError, AttributeError):
            for opt in self.stats_mode.options:
                if opt.default:
                    value = opt.value
                    break

        match value:
            case "quick":
                await self.stats_class.stats_quick(interaction)
            case "server":
                await self.stats_class.stats_server(interaction)
            case _:
                _msg = "This method isn't supported yet."
                await interaction.response.send_message(content=_msg, ephemeral=True, delete_after=5)

        await interaction.followup.delete_message(interaction.message.id)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
