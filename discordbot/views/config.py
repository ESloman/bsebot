import discord

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.views.config_salary import SalaryConfigView
from discordbot.views.config_threads import ThreadConfigView
from discordbot.views.config_valorant import ValorantConfigView
from discordbot.views.config_wordle import WordleConfigView

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

        match value:
            case "salary":
                msg, view = self._get_daily_minimum_message_and_view(interaction)
            case "threads":
                msg, view = self._get_thread_message_and_view(interaction)
            case "valorant":
                msg, view = self._get_valorant_message_and_view(interaction)
            case "wordle":
                msg, view = self._get_wordle_message_and_view(interaction)
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
                "on _which_ day.\n\n"
            )

        return msg, view

    def _get_wordle_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle wordle message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _chan = guild_db.get("wordle_channel")
        chan_mention = f"<#{_chan}>" if _chan else "_None_"
        view = WordleConfigView(guild_db["guild_id"])
        msg = (
            "**Wordle Config**\n\n"
            "Select the following options:\n"
            "1.) Whether doing the daily wordle is enabled or not\n"
            f"2.) If the above is true, which channel should the wordle be posted in? (Current: {chan_mention})\n"
            "3.) Whether to remind users to do their daily Wordle if they forget.\n\n"
            "You can leave channel select blank to keep current values."
        )
        return msg, view

    def _get_valorant_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """
        Handle valorant message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _chan = guild_db.get("valorant_channel")
        _role = guild_db.get("valorant_role")
        chan_mention = f"<#{_chan}>" if _chan else "_None_"
        role_mention = f"<@&{_role}>" if _role else "_None_"
        view = ValorantConfigView(interaction.guild_id)

        msg = (
            "**Valorant Config**\n\n"
            "Select the following options:\n"
            "1.) Whether to enable the daily vally rollcall\n"
            f"2.) If the above is true, which channel should the message be posted in? (Current: {chan_mention})\n"
            f"3.) Which role should be tagged in the message? (Current: {role_mention}).\n\n"
            "You can leave channel and role select blank to keep current values."
        )
        return msg, view

    def _get_daily_minimum_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """
        Handle daily minimum message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _min = guild_db.get("daily_minimum", 4)
        view = SalaryConfigView(_min)
        msg = (
            "**Salary Config**\n\n"
            "Select the daily minimum salary for users in this guild. This amount is deprecated by one each day for "
            "each user that doesn't interact with the guild. This is reset for the user upon interaction.\n\n"
        )
        return msg, view

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
