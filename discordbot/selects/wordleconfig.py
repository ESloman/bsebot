"""Wordle selects."""

import discord
from discord import Interaction, SelectOption

from discordbot.selects.bseselect import BSESelect
from mongo.datatypes.customs import EmojiDB


class WordleRootSelect(BSESelect):
    """Class for wordle root select."""

    selectable_options = ("wordle_config", "wordle_reactions", "wordle_reminders", "wordle_starting_words")

    def __init__(self, selectables: list[str] | None = None) -> None:
        """Initialisation method.

        Args:
            selectables (list[str] | None, optional): selectables. Defaults to None.
        """
        if not selectables:
            selectables = self.selectable_options

        options = [SelectOption(label=opt.replace("_", " ").title(), value=opt) for opt in selectables]

        super().__init__(options=options, placeholder="Configure...", min_values=1, max_values=1)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleChannelSelect(BSESelect):
    """Class for wordle channel select."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(
            discord.ComponentType.channel_select,
            placeholder="Select channel for daily Wordle message",
            channel_types=[discord.ChannelType.text, discord.ChannelType.private],
            min_values=1,
            max_values=1,
            disabled=True,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleActiveSelect(BSESelect):
    """Class for wordle active select."""

    def __init__(self, default: int | None = None) -> None:
        """Initialisation method.

        Args:
            default (int | None, optional): whether we're currently active or not. Defaults to None.
        """
        options = [
            SelectOption(label="Enabled", value="1", description="Do the wordle"),
            SelectOption(label="Disabled", value="0", description="Don't do the wordle"),
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

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleReminderSelect(BSESelect):
    """Class for wordle reminder select."""

    def __init__(self, default: int | None = None) -> None:
        """Initialisation method.

        Args:
            default (int | None, optional): whether we're currently enabled or not. Defaults to None.
        """
        options = [
            SelectOption(label="Enabled", value="1", description="Enable wordle reminders"),
            SelectOption(label="Disabled", value="0", description="Disable wordle reminders"),
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

        # expecting an update method on root here
        await self.view.update(interaction)


class WordleEmojiSelect(BSESelect):
    """Class for wordle emoji select."""

    def __init__(self, server_emojis: list[EmojiDB], score_num: str | None = None, current: str | None = None) -> None:
        """Initialisation method.

        Args:
            server_emojis (list[EmojiDB]): list of current server emojis
            score_num (str | None, optional): the score to select for. Defaults to None.
            current (str | None, optional): the current emoji for this score. Defaults to None.
        """
        options = [
            SelectOption(
                label=emoji.name,
                value=f"<:{emoji.name}:{emoji.eid}>",
                emoji=discord.PartialEmoji.from_str(f"{emoji.name}:{emoji.eid}"),
            )
            for emoji in server_emojis
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
            options=options,
        )

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected

        # expecting an update method on root here
        await self.view.update(interaction)
