"""Wordle config views."""

import contextlib

import discord
from bson import Int64

import discordbot.modals.wordle
from discordbot.selects.wordleconfig import (
    WordleActiveSelect,
    WordleChannelSelect,
    WordleEmojiSelect,
    WordleReminderSelect,
    WordleRootSelect,
)
from mongo.bsedataclasses import WordleReminders
from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.generic import DataStore
from mongo.bsepoints.guilds import Guilds


class WordleRootConfigView(discord.ui.View):
    """Class for wordle config root view."""

    def __init__(self, selectable_options: list[str] | None = None) -> None:
        """Initialisation method.

        Args:
            selectable_options (list[str] | None, optional): the selectable options. Defaults to None.
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.data_store = DataStore()
        self.wordle_config_select = WordleRootSelect(selectable_options)
        self.add_item(self.wordle_config_select)

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This timed out - please _place_ another one", view=None)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        wordle_config_val = None
        try:
            wordle_config_val = self.wordle_config_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.wordle_config_select.options:
                if opt.default:
                    wordle_config_val = opt.value
                    break

        if wordle_config_val:
            for child in self.children:
                if type(child) is discord.ui.Button and child.label == "Submit":
                    child.disabled = not wordle_config_val
                    break
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            wordle_config_val = self.wordle_config_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.wordle_config_select.options:
                if opt.default:
                    wordle_config_val = opt.value
                    break

        match wordle_config_val:
            case "wordle_config":
                guild_db = self.guilds.get_guild(interaction.guild_id)
                _chan = guild_db.wordle_channel
                chan_mention = f"<#{_chan}>" if _chan else "_None_"
                view = WordleConfigView(guild_db.guild_id)
                msg = (
                    "## Wordle Config\n\n"
                    "Select the following options:\n"
                    "-  Whether doing the daily wordle is enabled or not\n"
                    f"- If the above is true, which channel should the wordle be posted in? (Current: {chan_mention})\n"
                    "- Whether to remind users to do their daily Wordle if they forget.\n\n"
                    "You can leave channel select blank to keep current values."
                )
                await interaction.response.send_message(content=msg, view=view, ephemeral=True)
            case "wordle_reactions":
                view = WordleEmojiReactionConfigView(interaction.guild_id)
                msg = (
                    "## Wordle Emoji Reaction Config \n\n"
                    "Select which server emojis the bot uses to react to different Wordle scores.\n"
                    "If None are selected, the defaults will be used.\n\n"
                    "- X score\n"
                    "- 2 score\n"
                    "- 6 score\n"
                )
                await interaction.response.send_message(content=msg, view=view, ephemeral=True)
            case "wordle_reminders":
                modal = discordbot.modals.wordle.WordleReminderModal()
                await interaction.response.send_modal(modal)
            case "wordle_starting_words":
                words_result = self.data_store.get_starting_words()
                words = words_result["words"]
                modal = discordbot.modals.wordle.WordleStartingWords(words)
                await interaction.response.send_modal(modal)
            case _:
                return

        # delete the message now
        await interaction.followup.delete_message(interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)


class WordleConfigView(discord.ui.View):
    """Class for wordle config view."""

    def __init__(self, guild_id: int) -> None:
        """Initialisation method.

        Args:
            guild_id (int): the guild ID
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()

        guild_db = self.guilds.get_guild(guild_id)
        active = "1" if guild_db.wordle else "0"

        self.active_select = WordleActiveSelect(active)
        self.channel_select = WordleChannelSelect()

        if int(active):
            self.channel_select.disabled = False

        reminder = "1" if guild_db.wordle_reminders else "0"
        self.reminder_select = WordleReminderSelect(reminder)

        self.add_item(self.active_select)
        self.add_item(self.channel_select)
        self.add_item(self.reminder_select)

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This timed out - please _place_ another one", view=None)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        try:
            active_val = bool(int(self.active_select.values[0]))
        except (IndexError, AttributeError):
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        self.channel_select.disabled = not active_val
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:  # noqa: C901, PLR0912
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            active_val = bool(int(self.active_select.values[0]))
        except (IndexError, AttributeError):
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        channel = None
        try:
            channel = self.channel_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.channel_select.options:
                if opt.default:
                    channel = opt.value
                    break

        if channel and type(channel) not in {int, Int64}:
            channel = channel.id

        try:
            reminders = bool(int(self.reminder_select.values[0]))
        except (IndexError, AttributeError):
            for opt in self.reminder_select.options:
                if opt.default:
                    reminders = bool(int(opt.value))
                    break

        self.guilds.set_wordle_config(interaction.guild_id, active_val, channel, reminders)

        await interaction.response.edit_message(content="Wordle config updated.", view=None, delete_after=2)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)


class WordleEmojiReactionConfigView(discord.ui.View):
    """Class for wordle emoji reaction config view."""

    def __init__(self, guild_id: int) -> None:
        """Initialisation method.

        Args:
            guild_id (int): the guild ID
        """
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.emojis = ServerEmojis()

        guild_db = self.guilds.get_guild(guild_id)
        emoji_list = self.emojis.get_all_emojis(guild_id)

        current_x = guild_db.wordle_x_emoji
        current_two = guild_db.wordle_two_emoji
        current_six = guild_db.wordle_six_emoji

        self.x_select = WordleEmojiSelect(emoji_list, "X", current_x)
        self.two_select = WordleEmojiSelect(emoji_list, "2", current_two)
        self.six_select = WordleEmojiSelect(emoji_list, "6", current_six)

        self.add_item(self.x_select)
        self.add_item(self.two_select)
        self.add_item(self.six_select)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        x_val = None
        try:
            x_val = self.x_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.x_select.options:
                if opt.default:
                    x_val = opt.value
                    break

        two_val = None
        try:
            two_val = self.two_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.two_select.options:
                if opt.default:
                    two_val = opt.value
                    break

        six_val = None
        try:
            six_val = self.six_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.six_select.options:
                if opt.default:
                    six_val = opt.value
                    break

        self.guilds.update(
            {"guild_id": interaction.guild.id},
            {"$set": {"wordle_x_emoji": x_val, "wordle_two_emoji": two_val, "wordle_six_emoji": six_val}},
        )

        await interaction.response.edit_message(content="Wordle reaction emojis updated.", view=None, delete_after=2)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)


class WordleReminderConfirmView(discord.ui.View):
    """Class for wordle reminder config view."""

    def __init__(self, name: str) -> None:
        """Initialisation method.

        Args:
            name (str): the name
        """
        super().__init__(timeout=120)
        self.name = name
        self.wordle_reminders = WordleReminders()

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This timed out - please _place_ another one", view=None)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=False)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        all_reminders = self.wordle_reminders.get_all_reminders()
        reminder_names = [reminder["name"] for reminder in all_reminders]

        if self.name in reminder_names:
            # all our options existed already
            await interaction.response.edit_message(
                content="Your submission already existed - nothing has changed.",
                view=None,
                delete_after=3,
            )
            return

        self.wordle_reminders.insert_reminder(self.name, interaction.user.id)

        content = "Submitted your reminder to the database."

        await interaction.response.edit_message(content=content, view=None, delete_after=2)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, row=4, disabled=False)
    async def edit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        modal = discordbot.modals.wordle.WordleReminderModal(self.name)
        await interaction.response.send_modal(modal)
        await interaction.followup.delete_message(interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
