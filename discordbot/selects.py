import math

from discord import SelectOption, Interaction
from discord.ui import Select, View, Button

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
            options=options,
            custom_id="bet_select"
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

        outcome_select = [item for item in self.view.children if item.custom_id == "outcome_select"][0]
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
            if child.custom_id in ["amount_select", "submit_btn"]:
                child.disabled = True

        await interaction.response.edit_message(view=self.view)


class BetOutcomesSelect(Select):
    def __init__(self, outcomes: list, enable_id="amount_select"):
        """

        :param outcomes:
        """
        if not outcomes:
            outcomes = ["placeholder1", "placeholder2"]

        options = [
            SelectOption(label=opt) for opt in outcomes
        ]

        super().__init__(
            disabled=True,
            placeholder="Select an outcome",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="outcome_select"
        )

        # the item we need to enable when we get a value
        self.enable = enable_id

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_outcome = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_outcome

        for child in self.view.children:
            if child.custom_id == self.enable:
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)


class BetSelectAmount(Select):
    amounts = [
        1, 5, 10, 25, 50, 100, 250, 500, 750, 1000, 1500, 2000
    ]

    def __init__(self, user_eddies):
        """

        :param user_eddies:
        """

        options = [
            SelectOption(label=f"{opt}", value=f"{opt}") for opt in self.amounts
        ]
        options.append(
            SelectOption(
                label=f"{math.floor(user_eddies / 2)} - Half your eddies",
                value=f"{math.floor(user_eddies / 2)}")
        )
        options.append(
            SelectOption(label=f"{user_eddies} - ALL your eddies", value=f"{user_eddies}")
        )

        for opt in options:
            if int(opt.value) > user_eddies:
                options.remove(opt)

        options = sorted(options, key=lambda x: int(x.value))

        super().__init__(
            disabled=True,
            placeholder="Select amount of eddies to bet",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="amount_select"
        )

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        for child in self.view.children:
            if child.custom_id == "submit_btn":
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)
