
from discord import Interaction, SelectOption
from discord.ui import Select

from discordbot.selects.betamount import BetSelectAmount


class BetOutcomesSelect(Select):
    def __init__(self, outcomes: list, enable_type=BetSelectAmount):
        """

        :param outcomes:
        """
        if not outcomes:
            outcomes = ["placeholder1", "placeholder2"]
            options = [
                SelectOption(label=opt) for opt in outcomes
            ]
        else:
            options = outcomes

        super().__init__(
            disabled=not outcomes,
            placeholder="Select an outcome",
            min_values=1,
            max_values=1,
            options=options
        )

        # the item we need to enable when we get a value
        self.enable = enable_type

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_outcome = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_outcome

        for child in self.view.children:
            if type(child) == self.enable:
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)