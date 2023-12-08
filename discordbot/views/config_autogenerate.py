"""Autogenerate config views."""

import contextlib

import discord

from discordbot.modals.autogenerate import AddBet, AddCategory
from discordbot.selects.autogenerateconfig import AutogenerateCategorySelect, AutogenerateConfigSelect
from discordbot.utilities import PlaceHolderLogger
from mongo.bsepoints.guilds import Guilds


class AutoGenerateConfigView(discord.ui.View):
    """Class for autogenerate config view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.auto_config = AutogenerateConfigSelect()
        self.category_select = AutogenerateCategorySelect()

        self.add_item(self.auto_config)

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

    async def update(self, interaction: discord.Interaction) -> None:  # noqa: C901, PLR0912
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        try:
            auto_val = self.auto_config.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    auto_val = opt.value
                    break

        cat_val = None
        try:
            cat_val = self.category_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    cat_val = opt.value
                    break

        if auto_val == "category":
            # remove category select as we don't need it
            try:
                if len(self.children) > 3:  # noqa: PLR2004
                    self.remove_item(self.category_select)
            except Exception as exc:
                PlaceHolderLogger.debug(exc)

            for child in self.children:
                if type(child) is discord.ui.Button and child.label == "Submit":
                    child.disabled = False
                    break

        elif auto_val == "new":
            # add category select
            if len(self.children) < 4:  # noqa: PLR2004
                self.add_item(self.category_select)

            for child in self.children:
                if type(child) is discord.ui.Button and child.label == "Submit":
                    child.disabled = not bool(cat_val)
                    break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            auto_val = self.auto_config.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    auto_val = opt.value
                    break

        cat_val = None
        try:
            cat_val = self.category_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    cat_val = opt.value
                    break

        if auto_val == "category":
            modal = AddCategory()
            await interaction.response.send_modal(modal)
        elif auto_val == "new":
            modal = AddBet(cat_val)
            await interaction.response.send_modal(modal)

        await interaction.followup.delete_message(message_id=interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
