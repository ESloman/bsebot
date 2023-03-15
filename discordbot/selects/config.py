
from discord import Interaction, SelectOption
from discord.ui import Select


class ConfigSelect(Select):
    _values = [
        "Spoiler Threads"
    ]

    def __init__(self):

        options = [
            SelectOption(label=opt, value=opt.lower()) for opt in self._values
        ]

        super().__init__(
            disabled=False,
            placeholder="Select item to configure...",
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
