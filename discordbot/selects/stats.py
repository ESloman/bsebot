
import datetime

from discord import Interaction, SelectOption
from discord.ui import Select


class StatsModeSelect(Select):
    _modes = [
        ("Quick", "Your quick stats"),
        ("Server", "Server quick stats"),
        # ("Graphs", "Generate some graphs")
    ]  # type: tuple[str, str]

    def __init__(self):

        options = [
            SelectOption(
                label=opt[0],
                value=opt[0].lower(),
                default=True if opt == "Year" else False,
                description=opt[1]
            ) for opt in self._modes
        ]

        super().__init__(
            disabled=False,
            placeholder="Mode",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await self.view.update(interaction)


class StatsYearSelect(Select):
    _years = list(range(2021, datetime.datetime.now().year + 1))

    def __init__(self):
        options = [
            SelectOption(
                label=f"{opt}",
                value=f"{opt}",
                default=True if opt == self._years[-1] else False
            ) for opt in self._years
        ]

        super().__init__(
            disabled=False,
            placeholder="Year",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await self.view.update()
