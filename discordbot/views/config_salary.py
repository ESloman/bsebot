import discord

from discordbot.selects.salaryconfig import SalaryMinimumSelect
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class SalaryConfigView(discord.ui.View):
    def __init__(
        self,
        amount: int = None
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.user_points = UserPoints()

        self.min_select = SalaryMinimumSelect(amount)
        self.add_item(self.min_select)

    async def update(self):
        pass

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            amount = int(self.min_select._selected_values[0])
        except IndexError:
            # look for default as user didn't select one explicitly
            for opt in self.min_select.options:
                if opt.default:
                    amount = int(opt.value)
                    break

        old_min = self.guilds.get_daily_minimum(interaction.guild_id)

        # update users on current min to new min
        users = self.user_points.get_all_users_for_guild(interaction.guild_id)
        for user in users:
            if user.get("daily_minimum") == old_min:
                self.user_points.set_daily_minimum(user["uid"], interaction.guild_id, amount)

        # update server min
        self.guilds.set_daily_minimum(interaction.guild_id, amount)

        await interaction.response.edit_message(
            content="Daily minimum updated.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
