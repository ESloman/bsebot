"""Stats views."""

from typing import TYPE_CHECKING

import discord

from discordbot.selects.stats import StatsModeSelect
from discordbot.views.bseview import BSEView

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.stats import Stats


class StatsView(BSEView):
    """Class for stats view."""

    def __init__(
        self,
        stats_class: "Stats",
    ) -> None:
        """Initialisation method.

        Args:
            stats_class (discordbot.slashcommandeventclasses.stats.Stats): the stats class
        """
        super().__init__(timeout=None)

        self.stats_class: Stats = stats_class
        self.stats_mode = StatsModeSelect()

        self.add_item(self.stats_mode)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        value = self.get_select_value(self.stats_mode)
        self.toggle_button(not bool(value))
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=False)
    async def submit_button_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        value = self.get_select_value(self.stats_mode)

        match value:
            case "quick":
                await self.stats_class.stats_quick(interaction)
            case "server":
                await self.stats_class.stats_server(interaction)
            case _:
                _msg = "This method isn't supported yet."
                await interaction.response.send_message(content=_msg, ephemeral=True, delete_after=5)

        await interaction.followup.delete_message(interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
