"""Bless selects."""

from discord import Interaction, SelectOption
from discord.ui import Select


class BlessAmountSelect(Select):
    """Class for bless outcome select."""

    amounts = (100, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 10000)

    def __init__(self) -> None:
        """Initialisation method."""
        options = [SelectOption(label=f"{opt}", value=f"{opt}") for opt in self.amounts]

        super().__init__(
            disabled=False,
            placeholder="Select amount to bless people with.",
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

        await interaction.response.edit_message(view=self.view)


class BlessClassSelect(Select):
    """Class for bless classes."""

    values = (("all", "All the recently active server member"), ("supporters", "Your loyal followers only"))

    def __init__(self) -> None:
        """Initialisation method."""
        options = [SelectOption(label=opt[0], value=opt[0], description=opt[1]) for opt in self.values]

        super().__init__(
            disabled=False,
            placeholder="Select who should be blessed",
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

        await interaction.response.edit_message(view=self.view)
