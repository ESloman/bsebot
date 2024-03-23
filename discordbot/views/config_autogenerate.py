"""Autogenerate config views."""

import discord

from discordbot.modals.autogenerate import AddBet, AddCategory
from discordbot.selects.autogenerateconfig import AutogenerateCategorySelect, AutogenerateConfigSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds


class AutoGenerateConfigView(BSEView):
    """Class for autogenerate config view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.auto_config = AutogenerateConfigSelect()
        self.category_select = AutogenerateCategorySelect()

        self.add_item(self.auto_config)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        auto_val = self.get_select_value(self.auto_config)
        cat_val = self.get_select_value(self.category_select)

        if auto_val == "category":
            # remove category select as we don't need it
            try:
                if len(self.children) > 3:  # noqa: PLR2004
                    self.remove_item(self.category_select)
            except Exception as exc:
                self.logger.debug(exc)

            self.toggle_button(False, "Submit")

        elif auto_val == "new":
            # add category select
            if len(self.children) < 4:  # noqa: PLR2004
                self.add_item(self.category_select)

            self.toggle_button(not bool(cat_val), "Submit")

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        auto_val = self.get_select_value(self.auto_config)
        cat_val = self.get_select_value(self.category_select)

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
