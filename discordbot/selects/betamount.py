"""Bet amount select."""

import math

from discord import Interaction, SelectOption
from discord.ui import Button, Select


class BetSelectAmount(Select):
    """Class for bet amount selects."""

    amounts = (1, 5, 10, 25, 50, 75, 100, 175, 250, 500, 750, 1000, 1250, 1500, 1750, 2000)

    def __init__(self, user_eddies: int) -> None:
        """Initialisation method.

        Args:
            user_eddies (int): the amount of eddies the user has
        """
        options = [SelectOption(label=f"{opt}", value=f"{opt}") for opt in self.amounts]

        if user_eddies != 0:
            half_eddies = math.floor(user_eddies / 2)
            if half_eddies in self.amounts:
                opt = next(o for o in options if o.value == f"{half_eddies}")
                opt.label = f"{half_eddies} - Half your eddies"
            else:
                options.append(SelectOption(label=f"{half_eddies} - Half your eddies", value=f"{half_eddies}"))

            if user_eddies in self.amounts:
                opt = next(o for o in options if o.value == f"{user_eddies}")
                opt.label = f"{half_eddies} - ALL your eddies"
            else:
                options.append(SelectOption(label=f"{user_eddies} - ALL your eddies", value=f"{user_eddies}"))

        new_opts = [opt for opt in options if int(opt.value) <= int(user_eddies)]
        options = sorted(new_opts, key=lambda x: int(x.value))

        super().__init__(
            disabled=True,
            placeholder="Select amount of eddies to bet",
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

        for child in self.view.children:
            if type(child) is Button and child.label == "Submit":
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)
