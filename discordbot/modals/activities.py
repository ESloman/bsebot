
import discord

import discordbot.views.config_activities


class ActivityModal(discord.ui.Modal):
    def __init__(self, activity_type: str, placeholder_text: str, text_value: str = None, *args, **kwargs) -> None:
        super().__init__(*args, title="Enter activity text", **kwargs)

        self.activity_type = activity_type
        self.activity = discord.ui.InputText(label="Activity Text", placeholder=f"{placeholder_text}")

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

        activity = self.activity.value
        placeholder = self.activity.placeholder

        view = discordbot.views.config_activities.ActivityConfirmView(self.activity_type, placeholder, activity)

        msg = (
            "Your activity will appear as:\n\n"
            f"`{placeholder.strip('.')} {activity.strip()}`\n\n"
        )

        await interaction.followup.send(
            content=msg,
            ephemeral=True,
            view=view
        )
