
import discord

from discordbot.selects.salaryconfig import DailySalaryMessageSelect, DailySalarySummaryMessageSelect
from mongo.bsepoints.points import UserPoints


class DailyMessageView(discord.ui.View):
    def __init__(
        self,
        enabled: bool = False,
        is_admin: bool = False,
        summary_enabled: bool = False
    ):
        super().__init__(timeout=120)
        self.user_points = UserPoints()

        self.enabled_select = DailySalaryMessageSelect(enabled)
        self.add_item(self.enabled_select)

        self.summary_select = None
        if is_admin:
            # add summary message
            self.summary_select = DailySalarySummaryMessageSelect(summary_enabled)
            self.add_item(self.summary_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            enabled = self.enabled_select._selected_values[0]
        except (IndexError, AttributeError):
            # look for default as user didn't select one explicitly
            for opt in self.enabled_select.options:
                if opt.default:
                    enabled = opt.value
                    break

        enabled_bool = enabled == "enabled"

        if self.summary_select:
            try:
                summary_enabled = self.summary_select._selected_values[0]
            except (IndexError, AttributeError):
                # look for default as user didn't select one explicitly
                for opt in self.summary_select.options:
                    if opt.default:
                        summary_enabled = opt.value
                        break
            summary_bool = summary_enabled == "enabled"
        else:
            summary_bool = False

        if interaction.guild:
            # we have a guild - great
            guild_id = interaction.guild.id
        else:
            # handle where we don't have a guild
            guild_id = 0

        self.user_points.set_daily_eddies_toggle(interaction.user.id, guild_id, enabled_bool, summary_bool)

        msg = f"Daily salary message `{enabled}`."
        if self.summary_select:
            msg += f" Daily summary message `{summary_enabled}`."

        await interaction.response.edit_message(
            content=msg,
            view=None,
            delete_after=5
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
