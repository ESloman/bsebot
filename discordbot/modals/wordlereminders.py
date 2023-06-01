
import discord

import discordbot.views.config_wordle


class WordleReminderModal(discord.ui.Modal):
    def __init__(
        self,
        text_value: list[str] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, title="Submit wordle reminder text", **kwargs)

        self.placeholder = "Enter your reminder here.\nUse '{mention}' where you want the user to be mentioned."

        self.activity = discord.ui.InputText(
            label="Wordle Reminder Text",
            placeholder=self.placeholder,
            style=discord.InputTextStyle.multiline
        )

        if text_value:
            # set this to previously entered value
            self.activity.value = text_value

        self.add_item(self.activity)

    async def callback(self, interaction: discord.Interaction):
        """

        :param interaction:
        :return:
        """
        await interaction.response.defer(ephemeral=True)

        text = self.activity.value

        view = discordbot.views.config_wordle.WordleReminderConfirmView(text)

        msg = "Your reminder will appear as:\n\n"

        msg += text.format(mention=interaction.user.mention)

        await interaction.followup.send(
            content=msg,
            ephemeral=True,
            view=view
        )
