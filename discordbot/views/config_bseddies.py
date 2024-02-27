"""BSEddies config views."""

import discord
from bson import Int64

from discordbot.selects.bseddiesconfig import BSEddiesChannelSelect, BSEddiesRoleSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.guilds import Guilds


class BSEddiesConfigView(BSEView):
    """Class for BSEddies config view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.channel_select = BSEddiesChannelSelect()
        self.king_select = BSEddiesRoleSelect("KING")
        self.supporter_select = BSEddiesRoleSelect("Supporter Faction")
        self.revolutionary_select = BSEddiesRoleSelect("Revolutionary Faction")

        self.add_item(self.channel_select)
        self.add_item(self.king_select)
        self.add_item(self.supporter_select)
        self.add_item(self.revolutionary_select)

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
        update_dict = {}
        for key, select in [
            ("channel", self.channel_select),
            ("role", self.king_select),
            ("revolutionary_role", self.revolutionary_select),
            ("supporter_role", self.supporter_select),
        ]:
            value = self.get_select_value(select)
            if not value:
                continue
            value = int(value) if isinstance(value, str | int | Int64) else value.id
            update_dict[key] = value

        if update_dict:
            self.guilds.update({"guild_id": interaction.guild_id}, {"$set": update_dict})

        await interaction.response.edit_message(content="BSEddies config updated.", view=None, delete_after=5)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
