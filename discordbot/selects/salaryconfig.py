"""Salary config selects."""

from discord import Interaction, SelectOption
from discord.ui import Select


class SalaryMinimumSelect(Select):
    """Class for salary minimum select."""

    _amounts = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 50)

    def __init__(self, current_amount: int | None = None) -> None:
        """Initialisation method.

        Args:
            current_amount (int | None, optional): the current minimum. Defaults to None.
        """
        options = [SelectOption(label=str(a), value=str(a)) for a in self._amounts]

        if current_amount:
            for opt in options:
                if int(opt.value) == current_amount:
                    opt.default = True
                    break

        super().__init__(
            disabled=False,
            placeholder="Select minimum salary amount",
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


class DailySalaryMessageSelect(Select):
    """Class for daily salary message select."""

    def __init__(self, enabled: bool = False) -> None:
        """Initialisation method.

        Args:
            enabled (bool, optional): whether it's enabled or not. Defaults to False.
        """
        options = [
            SelectOption(label="Enabled", value="enabled", default=enabled),
            SelectOption(label="Disabled", value="disabled", default=not enabled),
        ]

        super().__init__(
            disabled=False,
            placeholder="Toggle daily salary message",
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


class DailySalarySummaryMessageSelect(Select):
    """Class for daily summary message select."""

    def __init__(self, enabled: bool = False) -> None:
        """Initialisation method.

        Args:
            enabled (bool, optional): whether it's enabled or not. Defaults to False.
        """
        options = [
            SelectOption(label="Enabled", value="enabled", default=enabled),
            SelectOption(label="Disabled", value="disabled", default=not enabled),
        ]

        super().__init__(
            disabled=False,
            placeholder="Toggle daily summary salary message",
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
