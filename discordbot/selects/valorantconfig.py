"""Valorant selects."""

import discord
from discord import Interaction, SelectOption
from discord.ui import Select


class ValorantChannelSelect(Select):
    """Class for valorant channel select."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(
            discord.ComponentType.channel_select,
            placeholder="Select channel for Valorant rollcalls",
            channel_types=[discord.ChannelType.text, discord.ChannelType.private],
            min_values=1,
            max_values=1,
            disabled=True,
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


class ValorantActiveSelect(Select):
    """Class for valorant active select."""

    def __init__(self, default: str | None = None) -> None:
        """Initialisation method.

        Args:
            default (int | None, optional): whether we're currently enabled or not. Defaults to None.
        """
        options = [
            SelectOption(label="Enabled", value="1", description="Enable Valorant rollcalls"),
            SelectOption(label="Disabled", value="0", description="Disable Valorant rollcalls"),
        ]

        if default:
            for opt in options:
                if opt.value == default:
                    opt.default = True
                    break

        super().__init__(
            disabled=False,
            placeholder="Whether Valorant rollcalls is enabled or not",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        # expecting an update method on root here
        await self.view.update(interaction)


class ValorantRoleSelect(Select):
    """Class for valorant role select."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(
            discord.ComponentType.role_select,
            placeholder="Select role for Valorant rollcalls",
            min_values=1,
            max_values=1,
            disabled=True,
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
