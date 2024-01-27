"""Stats selects."""

import datetime

import pytz
from discord import Interaction, SelectOption
from discord.ui import Select


class StatsModeSelect(Select):
    """Class for stats mode select."""

    _modes: tuple[tuple[str, str]] = (
        ("Quick", "Your quick stats"),
        ("Server", "Server quick stats"),
    )

    def __init__(self) -> None:
        """Initialisation method."""
        options = [
            SelectOption(
                label=opt[0],
                value=opt[0].lower(),
                default=opt == "Year",
                description=opt[1],
            )
            for opt in self._modes
        ]

        super().__init__(disabled=False, placeholder="Mode", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await self.view.update(interaction)


class StatsYearSelect(Select):
    """Class for stats year select."""

    _years = tuple(range(2021, datetime.datetime.now(tz=pytz.utc).year + 1))

    def __init__(self) -> None:
        """Initialisation method."""
        options = [SelectOption(label=f"{opt}", value=f"{opt}", default=opt == self._years[-1]) for opt in self._years]

        super().__init__(disabled=False, placeholder="Year", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await self.view.update()
