import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.selects.taxrate import TaxRateSelect

from mongo.bsepoints import UserPoints, Guilds


class TaxRateView(discord.ui.View):
    def __init__(self, current_tax: float, supporter_tax: float):
        super().__init__(timeout=None)
        self.tax_select = TaxRateSelect(current_tax, "notsupporter")
        self.supporter_tax_select = TaxRateSelect(supporter_tax, "supporter")
        self.add_item(self.tax_select)
        self.add_item(self.supporter_tax_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()

    def _append_to_history(self, user_id, guild_id, _type: ActivityTypes, **params):

        doc = {
            "type": _type,
            "timestamp": datetime.datetime.now(),
        }
        if params:
            doc["comment"] = f"Command parameters: {', '.join([f'{key}: {params[key]}' for key in params])}"

        doc["value"] = params["value"]
        self.user_points.append_to_activity_history(user_id, guild_id, doc)

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

        self._append_to_history(
            interaction.user.id, interaction.guild.id, ActivityTypes.BSEDDIES_ACTUAL_SET_TAX_RATE, value=value,
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

        if interaction.guild_id == BSE_SERVER_ID:
            channel = interaction.guild.get_channel(BSEDDIES_REVOLUTION_CHANNEL)
            msg = f"{interaction.user.mention} has changed the tax rate to `{value}`! 📈"
            await channel.send(content=msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
