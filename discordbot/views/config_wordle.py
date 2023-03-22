import discord


class WordleConfigView(discord.ui.View):
    def __init__(
        self
    ):
        super().__init__(timeout=120)

    @discord.ui.select(
            discord.ComponentType.channel_select,
            placeholder="Select channel for daily Wordle message",
            channel_types=[
                discord.ChannelType.text, discord.ChannelType.private
            ],
            row=3,
            max_values=1,
            min_values=1
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction) -> None:
        selected_amount = interaction.data["values"][0]
        for option in self.options:
            option.default = option.value == selected_amount
        await interaction.response.edit_message(view=self.view)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        [t for t in self.threads if str(t["thread_id"]) == self.thread_select._selected_values[0]][0]

        try:
            day = int(self.day_select._selected_values[0])
        except IndexError:
            # look for default as user didn't select one explicitly
            for opt in self.day_select.options:
                if opt.default:
                    day = int(opt.value)
                    break

        if day == 7:
            # 7 is for when user doesn't want a day set
            day = None

        try:
            bool(int(self.active_select._selected_values[0]))
        except IndexError:
            # user didn't select a value
            # true is default here
            pass

        await interaction.response.edit_message(
            content="Wordle config updated.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
