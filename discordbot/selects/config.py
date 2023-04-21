
from discord import Interaction, SelectOption
from discord.ui import Select


class ConfigSelect(Select):
    _values = [
        ("Admins", "admins"),
        ("Daily Salary", "salary"),
        ("Revolution Event", "revolution"),
        ("Spoiler Threads", "threads"),
        ("Valorant", "valorant"),
        ("Wordle Config", "wordle")
    ]

    def __init__(self):

        options = [
            SelectOption(label=opt[0], value=opt[1]) for opt in self._values
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
