"""Tax rate views."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.selects.taxrate import TaxRateSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class TaxRateView(BSEView):
    """Class for tax rate view."""

    def __init__(self, current_tax: float, supporter_tax: float) -> None:
        """Initialisation method.

        Args:
            current_tax (float): current tax rate
            supporter_tax (float): current supporter tax rate
        """
        super().__init__(timeout=None)
        self.tax_select = TaxRateSelect(current_tax, "notsupporter")
        self.supporter_tax_select = TaxRateSelect(supporter_tax, "supporter")
        self.add_item(self.tax_select)
        self.add_item(self.supporter_tax_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()
        self.activities = UserActivities()

    @discord.ui.button(label="Set Tax Rate", style=discord.ButtonStyle.blurple, emoji="📈", row=2)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        value = self.get_select_value(self.tax_select)
        value = float(value) if value is not None else 0.25

        supporter_value = self.get_select_value(self.supporter_tax_select)
        supporter_value = float(supporter_value) if supporter_value is not None else 0.1

        self.activities.add_activity(
            interaction.user.id,
            interaction.guild.id,
            ActivityTypes.BSEDDIES_ACTUAL_SET_TAX_RATE,
            value=value,
            supporter_value=supporter_value,
        )

        self.guilds.set_tax_rate(interaction.guild.id, value, supporter_value)
        self.guilds.update_tax_history(interaction.guild.id, value, supporter_value, interaction.user.id)
        msg = f"Successfully set peasant tax rate to **{value}** and supporter tax rate to **{supporter_value}**."
        await interaction.response.edit_message(content=msg, view=None)

        channel_id = self.guilds.get_channel(interaction.guild.id)
        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            msg = (
                f"{interaction.user.mention} has changed the tax rate to `{value}` "
                f"and the supporter tax rate to `{supporter_value}`! 📈"
            )
            await channel.send(content=msg)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
