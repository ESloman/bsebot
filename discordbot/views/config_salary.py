"""Salary config views."""

import discord

from discordbot.selects.salaryconfig import SalaryMinimumSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class SalaryConfigView(BSEView):
    """Class for salary config view."""

    def __init__(self, amount: int | None = None) -> None:
        """Initialisation method.

        Args:
            amount (int | None, optional): the current minimum amount. Defaults to None.
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.user_points = UserPoints()

        self.min_select = SalaryMinimumSelect(amount)
        self.add_item(self.min_select)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.
        """

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        amount = int(self.get_select_value(self.min_select))
        old_min = self.guilds.get_daily_minimum(interaction.guild_id)

        # update users on current min to new min
        users = self.user_points.get_all_users_for_guild(interaction.guild_id)
        for user in users:
            if user.daily_minimum == old_min:
                self.user_points.set_daily_minimum(user.uid, interaction.guild_id, amount)

        # update server min
        self.guilds.set_daily_minimum(interaction.guild_id, amount)

        await interaction.response.edit_message(content="Daily minimum updated.", view=None, delete_after=10)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
