
from discord import Interaction, SelectOption
from discord.ui import Button, Select

from discordbot.selects.betamount import BetSelectAmount
from discordbot.selects.betoutcomes import BetOutcomesSelect
from mongo.bsepoints import UserBets


class BetSelect(Select):
    def __init__(self, bets: list):
        """

        :param bets:
        """

        options = []
        for bet in bets:
            label = f"{bet['bet_id']} - {bet['title']}"
            if len(label) > 100:
                label = label[:99]
            options.append(
                SelectOption(
                    label=label,
                    value=f"{bet['bet_id']}",
                    description=bet['title']
                )
            )

        if len(bets) == 1:
            options[0].default = True

        super().__init__(
            placeholder="Select a bet",
            min_values=1,
            max_values=1,
            options=options
        )
        self.user_bets = UserBets()

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_bet = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_bet

        bet_obj = self.user_bets.get_bet_from_id(interaction.guild_id, selected_bet)
        outcomes = bet_obj["option_dict"]

        outcome_select = [item for item in self.view.children if type(item) == BetOutcomesSelect][0]
        outcome_select.options = [
            SelectOption(
                label=outcomes[key]["val"],
                value=key,
                emoji=key
            ) for key in outcomes
        ]
        outcome_select.disabled = False

        # disable the other ui elements when this changes
        for child in self.view.children:

            if type(child) == BetSelectAmount:
                child.disabled = True

            if type(child) == Button and child.label == "Submit":
                child.disabled = True

        await interaction.response.edit_message(view=self.view)