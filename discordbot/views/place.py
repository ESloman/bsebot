"""Place bet views."""

import contextlib

import discord

from discordbot.selects.bet import BetSelect
from discordbot.selects.betamount import BetSelectAmount
from discordbot.selects.betoutcomes import BetOutcomesSelect
from mongo.datatypes import Bet


class PlaceABetView(discord.ui.View):
    """Class for place bet view."""

    def __init__(self, bet_ids: list[Bet], user_eddies: int, submit_callback: callable) -> None:
        """Initialisation method.

        Args:
            bet_ids (list): the bet IDs
            user_eddies (int): the amount of user eddies
            submit_callback (callable): the submit callback function
        """
        super().__init__(timeout=60)
        self.add_item(BetSelect(bet_ids))

        if len(bet_ids) == 1 and "option_dict" in bet_ids[0]:
            outcomes = bet_ids[0]["option_dict"]
            options = [discord.SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]
        else:
            options = []

        self.add_item(BetOutcomesSelect(options))
        self.add_item(BetSelectAmount(user_eddies))

        self.submit_callback = submit_callback

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This `place` command timed out - please _place_ another one", view=None)

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
                except (IndexError, AttributeError):
                    # this means that this was default
                    data["bet_id"] = child.options[0].value
            elif type(child) is BetOutcomesSelect:
                data["emoji"] = child.values[0]
            elif type(child) is BetSelectAmount:
                data["amount"] = int(child.values[0])

        # call the callback that actually places the bet
        await self.submit_callback(interaction, data["bet_id"], data["amount"], data["emoji"])

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
