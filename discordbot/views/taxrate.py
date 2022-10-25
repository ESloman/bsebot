import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.selects import TaxRateSelect

from mongo.bsedataclasses import  TaxRate
from mongo.bsepoints import UserPoints


class TaxRateView(discord.ui.View):
    def __init__(self, current_tax: float):
        super().__init__(timeout=None)
        self.select = TaxRateSelect(current_tax)
        self.add_item(self.select)
        self.tax_rate = TaxRate()
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
            value = float(self.select.values[0])
        except (IndexError, AttributeError):
            value = float([o for o in self.select.options if o.default][0].value)
        
        self._append_to_history(
            interaction.user.id, interaction.guild.id, ActivityTypes.BSEDDIES_ACTUAL_SET_TAX_RATE, value=value
        )
        
        self.tax_rate.set_tax_rate(value)
        await interaction.response.edit_message(
            content=f"Successfully set tax rate to **{value}**.", 
            view=None
        )
        
        if interaction.guild_id == BSE_SERVER_ID:
            channel = interaction.guild.get_channel(BSEDDIES_REVOLUTION_CHANNEL)
            msg = f"{interaction.user.mention} has changed the tax rate to `{value}`! 📈"
            await channel.send(content=msg)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
