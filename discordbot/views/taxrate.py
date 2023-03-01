
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.selects.taxrate import TaxRateSelect

from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class TaxRateView(discord.ui.View):
    def __init__(self, current_tax: float, supporter_tax: float):
        super().__init__(timeout=None)
        self.tax_select = TaxRateSelect(current_tax, "notsupporter")
        self.supporter_tax_select = TaxRateSelect(supporter_tax, "supporter")
        self.add_item(self.tax_select)
        self.add_item(self.supporter_tax_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()
        self.activities = UserActivities()

    @discord.ui.button(label="Set Tax Rate", style=discord.ButtonStyle.blurple, emoji="📈", row=2)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        try:
            value = float(self.tax_select.values[0])
        except (IndexError, AttributeError):
            value = float([o for o in self.tax_select.options if o.default][0].value)

        try:
            supporter_value = float(self.supporter_tax_select.values[0])
        except (IndexError, AttributeError):
            supporter_value = float([o for o in self.supporter_tax_select.options if o.default][0].value)

        self.activities.add_activity(
            interaction.user.id,
            interaction.guild.id,
            ActivityTypes.BSEDDIES_ACTUAL_SET_TAX_RATE,
            value=value,
            supporter_value=supporter_value
        )

        self.guilds.set_tax_rate(interaction.guild.id, value, supporter_value)
        self.guilds.update_tax_history(interaction.guild.id, value, supporter_value, interaction.user.id)
        msg = (
            f"Successfully set peasant tax rate to **{value}** and supporter tax rate to **{supporter_value}**."
        )
        await interaction.response.edit_message(
            content=msg,
            view=None
        )

        channel_id = self.guilds.get_channel(interaction.guild.id)
        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            msg = f"{interaction.user.mention} has changed the tax rate to `{value}`! 📈"
            await channel.send(content=msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
