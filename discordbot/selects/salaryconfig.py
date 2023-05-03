
from discord import Interaction, SelectOption
from discord.ui import Select


class SalaryMinimumSelect(Select):
    _amounts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 50]

    def __init__(self, current_amount: int = None):
        options = [
            SelectOption(label=str(a), value=str(a)) for a in self._amounts
        ]

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

        await interaction.response.edit_message(view=self.view)


class DailySalaryMessageSelect(Select):
    def __init__(self, enabled: bool = False):
        options = [
            SelectOption(label="Enabled", value="enabled", default=enabled),
            SelectOption(label="Disabled", value="disabled", default=not enabled)
        ]

        super().__init__(
            disabled=False,
            placeholder="Toggle daily salary message",
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

        await interaction.response.edit_message(view=self.view)


class DailySalarySummaryMessageSelect(Select):
    def __init__(self, enabled: bool = False):
        options = [
            SelectOption(label="Enabled", value="enabled", default=enabled),
            SelectOption(label="Disabled", value="disabled", default=not enabled)
        ]

        super().__init__(
            disabled=False,
            placeholder="Toggle daily summary salary message",
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

        await interaction.response.edit_message(view=self.view)
