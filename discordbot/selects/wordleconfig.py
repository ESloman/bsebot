
import discord
from discord import Interaction, SelectOption
from discord.ui import Select

from mongo.datatypes import Emoji


class WordleRootSelect(Select):

    selectable_options = [
        "wordle_config",
        "wordle_reactions",
        "wordle_reminders",
        "wordle_starting_words"
    ]

    def __init__(self, selectables: list[str] = None):
        if not selectables:
            selectables = self.selectable_options

        options = [
            SelectOption(label=opt.replace("_", " ").title(), value=opt)
            for opt in selectables
        ]

        super().__init__(
            options=options,
            placeholder="Configure...",
            min_values=1,
            max_values=1
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


class WordleEmojiSelect(Select):
    def __init__(self, server_emojis: list[Emoji], score_num: str = None, current: str = None):

        options = [
            SelectOption(
                label=emoji["name"],
                value=f"<:{emoji['name']}:{emoji['eid']}>",
                emoji=discord.PartialEmoji.from_str(f"{emoji['name']}:{emoji['eid']}")
            ) for emoji in server_emojis
        ]

        if current:
            for opt in options:
                if opt.value == current:
                    opt.default = True

        super().__init__(
            placeholder=f"Select emoji for {score_num} reaction",
            min_values=0,
            max_values=1,
            disabled=False,
            options=options
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
