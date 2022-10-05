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


class BetSelectAmount(Select):
    amounts = [
        1, 5, 10, 25, 50, 75, 100, 175, 250, 500, 750, 1000, 1250, 1500, 1750, 2000
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

        new_opts = []
        for opt in options:
            if int(opt.value) <= int(user_eddies):
                new_opts.append(opt)

        options = sorted(new_opts, key=lambda x: int(x.value))

        super().__init__(
            disabled=True,
            placeholder="Select amount of eddies to bet",
            min_values=1,
            max_values=1,
            options=options
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
            if type(child) == Button and child.label == "Submit":
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)


class BetOutcomesSelect(Select):
    def __init__(self, outcomes: list, enable_type=BetSelectAmount):
        """

        :param outcomes:
        """
        if not outcomes:
            outcomes = ["placeholder1", "placeholder2"]
            options = [
                SelectOption(label=opt) for opt in outcomes
            ]
        else:
            options = outcomes

        super().__init__(
            disabled=not outcomes,
            placeholder="Select an outcome",
            min_values=1,
            max_values=1,
            options=options
        )

        # the item we need to enable when we get a value
        self.enable = enable_type

    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_outcome = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_outcome

        for child in self.view.children:
            if type(child) == self.enable:
                child.disabled = False
                break

        await interaction.response.edit_message(view=self.view)


class TaxRateSelect(Select):
    amounts = [
        5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 75
    ]

    def __init__(self, current_val: float):

        options = [
            SelectOption(label=f"{opt}%", value=f"{opt / 100}") for opt in self.amounts
        ]
        
        for option in options:
            if float(option.value) == current_val:
                option.default = True
                break

        super().__init__(
            disabled=False,
            placeholder="Select the global tax rate",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: Interaction):
        """

        :param interaction:
        :return:
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        await interaction.response.edit_message(view=self.view)