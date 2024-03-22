"""Bet amount select."""

import math

from discord import Interaction, SelectOption

from discordbot.selects.bseselect import BSESelect


class BetSelectAmount(BSESelect):
    """Class for bet amount selects."""

    min_amounts = (1, 5, 10, 25, 50, 75, 100, 250, 500, 1000, 5000)

    def __init__(self, user_eddies: int) -> None:
        """Initialisation method.

        We attempt to try and dynamically generate some amount options. We start with a base list;
        but we omit those that aren't greater than our user's eddies.

        Then, we round the user's eddies to whatever power of ten is most relevant (aka, 97 -> 100, 457 -> 500, etc,)
        and then step through every 10% of that and add that to the list of amounts. This generates some values for the
        users to use that is a bit more spread out and should scale automatically with the amount of eddies
        the user has.

        Args:
            user_eddies (int): the amount of eddies the user has
        """
        amounts = self._get_bet_amounts(user_eddies)
        options = [SelectOption(label=f"{opt}", value=f"{opt}") for opt in amounts]

        if user_eddies != 0:
            half_eddies = math.floor(user_eddies / 2)
            if half_eddies in amounts:
                opt = next(o for o in options if o.value == f"{half_eddies}")
                opt.label = f"{half_eddies} - Half your eddies"
            else:
                options.append(SelectOption(label=f"{half_eddies} - Half your eddies", value=f"{half_eddies}"))

            if user_eddies in amounts:
                opt = next(o for o in options if o.value == f"{user_eddies}")
                opt.label = f"{user_eddies} - ALL your eddies"
            else:
                options.append(SelectOption(label=f"{user_eddies} - ALL your eddies", value=f"{user_eddies}"))

        new_opts = [opt for opt in options if int(opt.value) <= int(user_eddies)]
        options = sorted(new_opts, key=lambda x: int(x.value))

        super().__init__(
            disabled=True,
            placeholder="Select amount of eddies to bet",
            min_values=1,
            max_values=1,
            options=options,
        )

    def _get_bet_amounts(self, user_eddies: int) -> list[int]:
        """Get bet amounts.

        Tries to dynamically select our bet amounts.

        Args:
            user_eddies (int): the eddies the user has

        Returns:
            list[int]: a list of amounts
        """
        amounts = [amount for amount in self.min_amounts if amount <= user_eddies]
        rounded = round(user_eddies, -int(math.floor(math.log10(abs(user_eddies)))))
        percs = (x / 10.0 for x in range(1, 10))
        for perc in percs:
            value = rounded * perc
            if value not in amounts:
                amounts.append(int(value))
        return amounts

    async def callback(self, interaction: Interaction) -> None:
        """Callback method.

        Args:
            interaction (Interaction): the interaction to callback to
        """
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount

        self.view.toggle_button(False, "Submit")
        await interaction.response.edit_message(view=self.view)
