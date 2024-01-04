"""Admin select."""

import discord
from discord import Interaction
from discord.ui import Select


class AdminUserSelect(Select):
    """The admin user select."""

    def __init__(self) -> None:
        """Initlisation method."""
        super().__init__(
            discord.ComponentType.user_select,
            placeholder="Select users to be admins",
            min_values=1,
            max_values=25,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)
