"""Wordle modal classes."""

import discord

import discordbot.views.config_wordle
from mongo.bsepoints.generic import DataStore


class WordleReminderModal(discord.ui.Modal):
    """Wordle reminder modal class."""

    def __init__(self, text_value: list[str] | None = None, *args: tuple[any], **kwargs: dict[any]) -> None:
        """Initilisation method.

        Args:
            text_value (list[str] | None, optional): the previously entered value(s). Defaults to None.
        """
        super().__init__(*args, title="Submit wordle reminder text", **kwargs)

        self.placeholder = "Enter your reminder here.\nUse '{mention}' where you want the user to be mentioned."

        self.activity = discord.ui.InputText(
            label="Wordle Reminder Text",
            placeholder=self.placeholder,
            style=discord.InputTextStyle.multiline,
        )

        if text_value:
            # set this to previously entered value
            self.activity.value = text_value

        self.add_item(self.activity)

    async def callback(self, interaction: discord.Interaction) -> None:
        """The submit callback.

        Args:
            interaction (discord.Interaction): the interaction
        """
        await interaction.response.defer(ephemeral=True)

        text = self.activity.value

        view = discordbot.views.config_wordle.WordleReminderConfirmView(text)

        msg = "Your reminder will appear as:\n\n"

        msg += text.format(mention=interaction.user.mention)

        await interaction.followup.send(content=msg, ephemeral=True, view=view)


class WordleStartingWords(discord.ui.Modal):
    """Wordle starting words modal class."""

    def __init__(self, current_words: list[str] | None = None, *args: tuple[any], **kwargs: tuple[any]) -> None:
        """Initialisation method.

        Args:
            current_words (list[str] | None, optional): current starting words list. Defaults to None.
        """
        super().__init__(*args, title="Set wordle starting words", **kwargs)

        self.data_store = DataStore()

        placeholder = "Enter your reminder here.\nUse '{mention}' where you want the user to be mentioned."

        self.activity = discord.ui.InputText(
            label="Wordle Reminder Text",
            placeholder=placeholder,
            style=discord.InputTextStyle.multiline,
        )

        if current_words:
            # set this to previously entered values
            text = "\n".join(current_words)
            self.activity.value = text

        self.add_item(self.activity)

    async def callback(self, interaction: discord.Interaction) -> None:
        """Submit button callback.

        Args:
            interaction (discord.Interaction): the interaction
        """
        await interaction.response.defer(ephemeral=True)

        text = self.activity.value
        words = text.split("\n")

        self.data_store.set_starting_words(words)

        await interaction.followup.send(
            content="Submitted.",
            ephemeral=True,
        )
