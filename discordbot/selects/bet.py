"""Bet selects."""

from discord import Interaction, SelectOption

from discordbot.constants import BET_TITLE_DISPLAY_LENTH
from discordbot.selects.betamount import BetAmountSelect
from discordbot.selects.betoutcomes import BetOutcomesSelect
from discordbot.selects.bseselect import BSESelect
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB


class BetSelect(BSESelect):
    """Class for Bet select."""

    def __init__(self, bets: list[BetDB]) -> None:
        """Initialisation method."""
        options = []
        for bet in bets:
            title = bet.title
            if len(bet.title) > BET_TITLE_DISPLAY_LENTH:
                title = title[:99]
            label = f"{bet.bet_id} - {title}"
            if len(label) > BET_TITLE_DISPLAY_LENTH:
                label = label[:99]

            options.append(SelectOption(label=label, value=f"{bet.bet_id}", description=title))

        if len(bets) == 1:
            options[0].default = True

        super().__init__(placeholder="Select a bet", min_values=1, max_values=1, options=options)
        self.user_bets = UserBets()

    def _enable_outcome_select(self, outcome_select: BetOutcomesSelect, bet: BetDB) -> None:
        """Enable the outcome select."""
        outcomes = bet.option_dict
        outcome_select.options = [SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]
        outcome_select.disabled = False
        # disable the other ui elements when this changes
        self.view.toggle_button(True, "Submit")
        self.view.toggle_item(True, BetAmountSelect)

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_bet = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_bet

        bet_db = self.user_bets.get_bet_from_id(interaction.guild_id, selected_bet)

        try:
            outcome_select = next(item for item in self.view.children if type(item) is BetOutcomesSelect)
        except StopIteration:
            self.view.toggle_button(False, "Submit")
        else:
            self._enable_outcome_select(outcome_select, bet_db)
