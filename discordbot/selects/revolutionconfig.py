"""Revolution config selects."""

from discord import Interaction, SelectOption

from discordbot.selects.bseselect import BSESelect


class RevolutionEnableSelect(BSESelect):
    """Class for revolution enable select."""

    def __init__(self, enabled: bool = True) -> None:
        """Initialisation method.

        Args:
            enabled (bool, optional): whether we're already enabled or not. Defaults to True.
        """
        options = [
            SelectOption(label="Enabled", value="enabled", default=enabled),
            SelectOption(label="Disabled", value="disabled", default=not enabled),
        ]

        super().__init__(
            disabled=False,
            placeholder="Whether revolution event is enabled/disabled",
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

        await interaction.response.edit_message(view=self.view)
