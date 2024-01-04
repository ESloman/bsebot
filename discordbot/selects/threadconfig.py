"""Thread config selects."""

from discord import Interaction, SelectOption
from discord.ui import Select

from discordbot.constants import BET_TITLE_DISPLAY_LENTH
from mongo.datatypes import Thread


class ThreadConfigSelect(Select):
    """Class for thread config select."""

    def __init__(self, threads: list[Thread]) -> None:
        """Initialisation method.

        Args:
            threads (list[Thread]): the list of threads to configure
        """
        options = []
        for thread in threads:
            label = thread.name
            if len(label) > BET_TITLE_DISPLAY_LENTH:
                label = label[:99]

            value = str(thread.thread_id)
            opt = SelectOption(label=label, value=value)
            options.append(opt)

        super().__init__(
            disabled=False,
            placeholder="Select thread to configure...",
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

        await self.view.update()
        await interaction.response.edit_message(view=self.view)


class ThreadActiveSelect(Select):
    """Class for active select."""

    def __init__(self) -> None:
        """Initialisation method."""
        options = [
            SelectOption(label="Active", value="1", description="Send spoiler messages", default=True),
            SelectOption(label="Inactive", value="0", description="Don't send spoiler messages"),
        ]

        super().__init__(
            disabled=True,
            placeholder="Select thread activity",
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


class ThreadDaySelect(Select):
    """Class for day select."""

    def __init__(self) -> None:
        """Initialisation method."""
        options = [
            SelectOption(label="Monday", value="0"),
            SelectOption(label="Tuesday", value="1"),
            SelectOption(label="Wednesday", value="2"),
            SelectOption(label="Thursday", value="3"),
            SelectOption(label="Friday", value="4"),
            SelectOption(label="Saturday", value="5"),
            SelectOption(label="Sunday", value="6"),
            SelectOption(label="None", value="7"),
        ]

        super().__init__(
            disabled=True,
            placeholder="Select a day to send mute reminders",
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
