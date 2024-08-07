"""Place bet views."""

from typing import TYPE_CHECKING

import discord

from discordbot.selects.bet import BetSelect
from discordbot.selects.betamount import BetAmountSelect
from discordbot.selects.betoutcomes import BetOutcomesSelect
from discordbot.views.bseview import BSEView
from mongo.datatypes.bet import BetDB

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.place import PlaceBet


class PlaceABetView(BSEView):
    """Class for place bet view."""

    def __init__(self, bets: list[BetDB], user_eddies: int, place: "PlaceBet") -> None:
        """Initialisation method.

        Args:
            bets (list): the bets
            user_eddies (int): the amount of user eddies
            place (PlaceBet): the submit callback function
        """
        super().__init__(timeout=60)
        self.add_item(BetSelect(bets))

        if len(bets) == 1 and bets[0].option_dict:
            outcomes = bets[0].option_dict
            options = [discord.SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]
        else:
            options = []

        self.add_item(BetOutcomesSelect(options))
        self.add_item(BetAmountSelect(user_eddies))

        self.place: PlaceBet = place

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True, emoji="💰")
    async def submit_button_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        data = {}
        for child in self.children:
            if type(child) is BetSelect:
                try:
                    data["bet_id"] = child.values[0]
                except (IndexError, AttributeError, TypeError):
                    # this means that this was default
                    data["bet_id"] = child.options[0].value
            elif type(child) is BetOutcomesSelect:
                data["emoji"] = child.values[0]
            elif type(child) is BetAmountSelect:
                data["amount"] = int(child.values[0])

        # call the callback that actually places the bet
        await self.place.place_bet(interaction, data["bet_id"], data["amount"], data["emoji"])

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
