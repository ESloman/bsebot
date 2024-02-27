"""Tax rate selects."""

from discord import Interaction, SelectOption

from discordbot.selects.bseselect import BSESelect


class TaxRateSelect(BSESelect):
    """Class for tax rate select."""

    _amounts = (5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90)

    def __init__(self, current_val: float, tax_type: str) -> None:
        """Initialisation method."""
        if tax_type == "supporter":
            placeholder = "Select supporter tax rate"
            amounts = list(range(0, 100, 5))
        else:
            placeholder = "Select peasant tax rate"
            amounts = self._amounts

        options = [SelectOption(label=f"{opt}%", value=f"{opt / 100}" if opt != 0 else "0.0") for opt in amounts]

        for option in options:
            if float(option.value) == current_val:
                option.default = True
                break

        super().__init__(disabled=False, placeholder=placeholder, min_values=1, max_values=1, options=options)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await interaction.response.edit_message(view=self.view)
