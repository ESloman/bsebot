"""Admin configuration views."""

import discord

from discordbot.selects.adminconfig import AdminUserSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds


class AdminConfigView(BSEView):
    """Class for admin config view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.admins_select = AdminUserSelect()
        self.add_item(self.admins_select)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        selected = self.admins_select.values

        for child in self.children:
            if type(child) is discord.ui.Button and child.label == "Submit":
                child.disabled = not bool(selected)
                break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        selected = self.admins_select.values

        user_ids = [user.id for user in selected]

        self.guilds.update({"guild_id": interaction.guild_id}, {"$set": {"admins": user_ids}})

        admins = ", ".join([f"<@{a}>" for a in user_ids])

        await interaction.response.edit_message(
            content=f"Admins updated. New admins: {admins}",
            view=None,
            delete_after=10,
        )

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
