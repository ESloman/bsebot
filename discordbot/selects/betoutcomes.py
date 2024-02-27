"""Bet outcome select."""

from discord import Interaction, SelectOption

from discordbot.selects.betamount import BetSelectAmount
from discordbot.selects.bseselect import BSESelect


class BetOutcomesSelect(BSESelect):
    """Class for bet outcomes."""

    def __init__(self, outcomes: list[SelectOption], enable_type: type = BetSelectAmount, close: bool = False) -> None:
        """Initialisation method.

        Args:
            outcomes (list): the possible outcomes
            enable_type (type, optional): the select type. Defaults to BetSelectAmount.
            close (bool, optional): whether we're closing the bet or not. Defaults to False.
        """
        if not outcomes:
            outcomes = ["placeholder1", "placeholder2"]
            options = [SelectOption(label=opt) for opt in outcomes]
        else:
            options = outcomes

        super().__init__(
            disabled=not outcomes,
            placeholder="Select an outcome",
            min_values=1,
            max_values=len(options) if close else 1,
            options=options,
        )

        # the item we need to enable when we get a value
        self.enable_type: type = enable_type

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_outcomes = interaction.data["values"]
        for option in self.options:
            option.default = option.value in selected_outcomes

        self.view.toggle_item(False, self.enable_type)
        await interaction.response.edit_message(view=self.view)
