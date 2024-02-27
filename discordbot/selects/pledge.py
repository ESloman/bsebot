"""Pledge selects."""

from discord import Interaction, SelectOption

from discordbot.bot_enums import SupporterType
from discordbot.selects.bseselect import BSESelect


class PledgeSelect(BSESelect):
    """Class for pledge type select."""

    _values = ("Neutral", "Supporter", "Revolutionary")

    def __init__(self, current: SupporterType) -> None:
        """Initialisation method.

        Args:
            current (SupporterType): the current supporter type
        """
        options = [SelectOption(label=opt, value=opt.lower()) for opt in self._values]

        for option in options:
            if option.value == self._values[current].lower():
                option.default = True
                break

        super().__init__(disabled=False, placeholder="Select your side", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await interaction.response.edit_message(view=self.view)
