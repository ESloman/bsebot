import discord

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.views.config_threads import ThreadConfigView

from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.guilds import Guilds


class ConfigView(discord.ui.View):
    def __init__(
        self,
    ):
        super().__init__(timeout=120)
        self.spoiler_threads = SpoilerThreads()
        self.guilds = Guilds()
        self.config_select = ConfigSelect()
        self.add_item(self.config_select)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        value = self.config_select._selected_values[0]
        await interaction.response.edit_message(
            content="Loading your config option now...",
            view=None,
            delete_after=2
        )

        match int(value):
            case 0:
                # 0 is for threads
                msg, view = self._get_thread_message_and_view(interaction)
            case _:
                # default case
                msg = "unknown"
                view = None

        try:
            await interaction.followup.send(msg, ephemeral=True, view=view)
        except AttributeError:
            await interaction.followup.send(msg, ephemeral=True)

    def _get_thread_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """
        Handle thread message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """

        threads = self.spoiler_threads.get_all_threads(interaction.guild_id)
        threads = [
            t for t in threads
            if (t.get("owner", t.get("creator", CREATOR)) == interaction.user.id or interaction.user.id == CREATOR)
            and t.get("active")
        ]

        if not threads:
            view = None
            msg = "No available threads for you to configure."

        else:
            view = ThreadConfigView(threads)
            msg = (
                "_Thread Configuration_\n"
                "Select a thread to configure, and then select whether it should send mute reminders and "
                "on _which_ day."
            )

        return msg, view

    def _get_wordle_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """_summary_

        Args:
            interaction (discord.Interaction): _description_

        Returns:
            tuple[str, discord.ui.View]: _description_
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        guild_db["wordle_channel"]


    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
