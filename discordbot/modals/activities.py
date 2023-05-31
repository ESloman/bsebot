
import discord

import discordbot.views.config_activities


class ActivityModal(discord.ui.Modal):
    def __init__(
        self,
        activity_type: str,
        placeholder_text: str,
        text_value: list[str] = None,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, title="Enter activity text", **kwargs)

        self.activity_type = activity_type
        self.placeholder = placeholder_text

        placeholder = self.placeholder + "\nEnter multiple entries on different lines"
        self.activity = discord.ui.InputText(
            label="Activity Text",
            placeholder=f"{placeholder}",
            style=discord.InputTextStyle.multiline
        )

        if text_value:
            # set this to previously entered value
            self.activity.value = "\n".join(text_value)

        self.add_item(self.activity)

    async def callback(self, interaction: discord.Interaction):
        """

        :param interaction:
        :return:
        """
        await interaction.response.defer(ephemeral=True)

        activity = self.activity.value
        activity = activity.split("\n")

        view = discordbot.views.config_activities.ActivityConfirmView(self.activity_type, self.placeholder, activity)

        _act = "activity" if len(activity) == 1 else "activities"
        msg = f"Your {_act} will appear as:\n\n"
        for act in activity:
            msg += f"- `{self.placeholder.strip('.')} {act.strip()}`\n"

        await interaction.followup.send(
            content=msg,
            ephemeral=True,
            view=view
        )
