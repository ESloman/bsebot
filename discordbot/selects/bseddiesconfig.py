"""BSEddies selects."""

import discord
from discord import Interaction
from discord.ui import Select


class BSEddiesChannelSelect(Select):
    """Class for BSEddies channel select."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(
            discord.ComponentType.channel_select,
            placeholder="Select channel for BSEddies stuff",
            channel_types=[discord.ChannelType.text, discord.ChannelType.private],
            min_values=0,
            max_values=1,
            disabled=False,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        try:
            selected = interaction.data["values"][0]
        except (IndexError, AttributeError):
            # nothing selected
            selected = None

        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)


class BSEddiesRoleSelect(Select):
    """Class for BSEddies role select."""

    def __init__(self, role_type: str = "KING") -> None:
        """Initialisation method.

        Args:
            role_type (str, optional): the role type. Defaults to "KING".
        """
        super().__init__(
            discord.ComponentType.role_select,
            placeholder=f"Select role for the {role_type}",
            min_values=0,
            max_values=1,
            disabled=False,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        try:
            selected = interaction.data["values"][0]
        except (IndexError, AttributeError):
            # nothing selected
            selected = None

        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)
