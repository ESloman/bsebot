"""Activity selects."""

from discord import Interaction, SelectOption

from discordbot.selects.bseselect import BSESelect


class ActivityTypeSelect(BSESelect):
    """Class for Activity Type select."""

    def __init__(self) -> None:
        """Initialisation."""
        options = [
            SelectOption(label=option[0], value=option[1])
            for option in [("Listening", "listening"), ("Playing", "playing"), ("Watching", "watching")]
        ]

        super().__init__(
            disabled=False,
            placeholder="Select the activity type",
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

        await self.view.update(interaction)
