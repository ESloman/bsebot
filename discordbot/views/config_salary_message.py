"""Salary messages config view."""

import discord

from discordbot.selects.salaryconfig import DailySalaryMessageSelect, DailySalarySummaryMessageSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.points import UserPoints


class DailyMessageView(BSEView):
    """Class for daily message config view."""

    def __init__(self, enabled: bool = False, is_admin: bool = False, summary_enabled: bool = False) -> None:
        """Initialisation method.

        Args:
            enabled (bool, optional): whether we're currently enabled. Defaults to False.
            is_admin (bool, optional): whether the user is admin or not. Defaults to False.
            summary_enabled (bool, optional): whether the summary is enabled or not. Defaults to False.
        """
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
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            enabled = self.enabled_select._selected_values[0]  # noqa: SLF001
        except (IndexError, AttributeError, TypeError):
            # look for default as user didn't select one explicitly
            for opt in self.enabled_select.options:
                if opt.default:
                    enabled = opt.value
                    break

        enabled_bool = enabled == "enabled"

        if self.summary_select:
            try:
                summary_enabled = self.summary_select._selected_values[0]  # noqa: SLF001
            except (IndexError, AttributeError, TypeError):
                # look for default as user didn't select one explicitly
                for opt in self.summary_select.options:
                    if opt.default:
                        summary_enabled = opt.value
                        break
            summary_bool = summary_enabled == "enabled"
        else:
            summary_bool = False

        guild_id = interaction.guild.id if interaction.guild else 0
        self.user_points.set_daily_eddies_toggle(interaction.user.id, guild_id, enabled_bool, summary_bool)

        msg = f"Daily salary message `{enabled}`."
        if self.summary_select:
            msg += f" Daily summary message `{summary_enabled}`."

        await interaction.response.edit_message(content=msg, view=None, delete_after=5)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
