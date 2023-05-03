import discord

from discordbot.selects.revolutionconfig import RevolutionEnableSelect
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class RevolutionConfigView(discord.ui.View):
    def __init__(
        self,
        enabled: bool = True
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.user_points = UserPoints()

        self.enabled_select = RevolutionEnableSelect(enabled)
        self.add_item(self.enabled_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            enabled = self.enabled_select._selected_values[0]
        except IndexError:
            # look for default as user didn't select one explicitly
            for opt in self.enabled_select.options:
                if opt.default:
                    enabled = opt.value
                    break

        enabled_bool = enabled == "enabled"

        self.guilds.set_revolution_toggle(interaction.guild_id, enabled_bool)

        await interaction.response.edit_message(
            content=f"Revolution event {enabled}",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
