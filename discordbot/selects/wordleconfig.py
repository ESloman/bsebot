
import discord
from discord import Interaction, SelectOption
from discord.ui import Select


class WordleChannelSelect(Select):
    def __init__(self):
        super().__init__(
            discord.ComponentType.channel_select,
            placeholder="Select channel for daily Wordle message",
            channel_types=[
                discord.ChannelType.text, discord.ChannelType.private
            ],
            min_values=1,
            max_values=1,
            disabled=True
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleActiveSelect(Select):
    def __init__(self, default=None):
        options = [
            SelectOption(label="Enabled", value="1", description="Do the wordle"),
            SelectOption(label="Disabled", value="0", description="Don't do the wordle")
        ]

        if default:
            for opt in options:
                if opt.value == default:
                    opt.default = True
                    break

        super().__init__(
            disabled=False,
            placeholder="Whether doing the wordle is enabled or not",
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

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleReminderSelect(Select):
    def __init__(self, default=None):
        options = [
            SelectOption(label="Enabled", value="1", description="Enable wordle reminders"),
            SelectOption(label="Disabled", value="0", description="Disable wordle reminders")
        ]

        if default:
            for opt in options:
                if opt.value == default:
                    opt.default = True
                    break

        super().__init__(
            disabled=False,
            placeholder="Whether wordle reminders are enabled or not",
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

        # expecting an update method on root here
        await self.view.update(interaction)