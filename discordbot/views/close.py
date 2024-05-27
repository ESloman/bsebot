"""Close views."""

from typing import TYPE_CHECKING

import discord

from discordbot.selects.bet import BetSelect
from discordbot.selects.betoutcomes import BetOutcomesSelect
from discordbot.views.bseview import BSEView
from mongo.datatypes.bet import BetDB

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.close import CloseBet


class CloseABetView(BSEView):
    """Class for closing a bet view."""

    def __init__(self, bets: list[BetDB], close: "CloseBet") -> None:
        """Initialisation method.

        Args:
            bets (list[Bet]): the list of available bet IDs
            close (CloseBet): the close class
        """
        super().__init__(timeout=60)
        self.bet_select = BetSelect(bets)
        self.add_item(self.bet_select)

        if len(bets) == 1 and bets[0].option_dict:
            outcomes = bets[0].option_dict
            options = [discord.SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]
        else:
            options = []

        self.bet_outcome_select = BetOutcomesSelect(options, discord.ui.Button, True)
        self.add_item(self.bet_outcome_select)
        self.close: CloseBet = close

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def submit_button_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        bet_id = self.get_select_value(self.bet_select)
        emoji = self.get_select_value(self.bet_outcome_select)

        # call the callback that actually closes the bet
        await self.close.close_bet(interaction, bet_id, emoji)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
