
import discord

from discordbot.selects.giftamount import GiftAmount
from discordbot.slashcommandeventclasses.gift import Gift


class GiftUserEddiesView(discord.ui.View):
    def __init__(self, user_eddies: int, friend: discord.Member, gift: Gift):
        super().__init__(timeout=120)

        self.gift = gift
        self.friend = friend
        self.gift_amount = GiftAmount(user_eddies)
        self.add_item(self.gift_amount)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        try:
            await self.message.edit(content="This command timed out - please _place_ another one", view=None)
        except discord.NotFound:
            # not found is when the message has already been deleted
            # don't need to edit in that case
            pass

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True)
    async def submit_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        try:
            value = self.gift_amount.values[0]
        except (IndexError, AttributeError):
            value = [o for o in self.gift_amount.options if o.default][0].value

        await self.gift.gift_eddies(interaction, self.friend, int(value))
        await interaction.followup.edit_message(interaction.message.id, view=None, content="Done.")

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=5)
