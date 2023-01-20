
from discord import Interaction, SelectOption
from discord.ui import Select


class TaxRateSelect(Select):
    amounts = [
        5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 75
    ]

    def __init__(self, current_val: float):

        options = [
            SelectOption(label=f"{opt}%", value=f"{opt / 100}") for opt in self.amounts
        ]

        for option in options:
            if float(option.value) == current_val:
                option.default = True
                break

        super().__init__(
            disabled=False,
            placeholder="Select the global tax rate",
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
