"""Close views."""

from typing import TYPE_CHECKING

import discord

from discordbot.selects.bet import BetSelect
from discordbot.selects.betoutcomes import BetOutcomesSelect
from mongo.datatypes.bet import BetDB

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.close import CloseBet


class CloseABetView(discord.ui.View):
    """Class for closing a bet view."""

    def __init__(self, bets: list[BetDB], close: "CloseBet") -> None:
        """Initialisation method.

        Args:
            bets (list[Bet]): the list of available bet IDs
            close (CloseBet): the close class
        """
        super().__init__(timeout=60)
        self.add_item(BetSelect(bets))

        if len(bets) == 1 and bets[0].option_dict:
            outcomes = bets[0].option_dict
            options = [discord.SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]
        else:
            options = []

        self.add_item(BetOutcomesSelect(options, discord.ui.Button, True))
        self.close: "CloseBet" = close

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True)
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
                data["emoji"] = child.values

        # call the callback that actually places the bet
        await self.close.close_bet(interaction, data["bet_id"], data["emoji"])

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
