"""User gift views."""

import discord

from discordbot.selects.giftamount import GiftAmount
from discordbot.slashcommandeventclasses.gift import Gift
from discordbot.views.bseview import BSEView


class GiftUserEddiesView(BSEView):
    """Class for user eddies gift view."""

    def __init__(self, user_eddies: int, friend: discord.Member, gift: Gift) -> None:
        """Initialisation method.

        Args:
            user_eddies (int): the amount of eddies the user has
            friend (discord.Member): the giftee
            gift (Gift): the gift class
        """
        super().__init__(timeout=120)

        self.gift = gift
        self.friend = friend
        self.gift_amount = GiftAmount(user_eddies)
        self.add_item(self.gift_amount)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True)
    async def submit_button_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            value = self.gift_amount.values[0]
        except (IndexError, AttributeError, TypeError):
            value = next(o for o in self.gift_amount.options if o.default).value

        await self.gift.gift_eddies(interaction, self.friend, int(value))
        await interaction.followup.edit_message(interaction.message.id, view=None, content="Done.")

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
