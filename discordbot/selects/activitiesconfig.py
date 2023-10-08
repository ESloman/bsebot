
from discord import Interaction, SelectOption
from discord.ui import Select


class ActivityTypeSelect(Select):
    def __init__(self):

        options = [
            SelectOption(label=option[0], value=option[1]) for option in
            [
                ("Listening", "listening"),
                ("Playing", "playing"),
                ("Watching", "watching")
            ]
        ]

        super().__init__(
            disabled=False,
            placeholder="Select the activity type",
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
