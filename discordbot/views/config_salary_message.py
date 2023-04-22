
import discord

from discordbot.selects.salaryconfig import DailySalaryMessageSelect
from mongo.bsepoints.points import UserPoints


class DailyMessageView(discord.ui.View):
    def __init__(
        self,
        enabled: bool = False
    ):
        super().__init__(timeout=120)
        self.user_points = UserPoints()

        self.enabled_select = DailySalaryMessageSelect(enabled)
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

        if interaction.guild:
            # we have a guild - great
            guild_id = interaction.guild.id
        else:
            # handle where we don't have a guild
            guild_id = 0

        self.user_points.set_daily_eddies_toggle(interaction.user.id, guild_id, enabled_bool)

        await interaction.response.edit_message(
            content=f"Daily salary message `{enabled}`.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=10)
