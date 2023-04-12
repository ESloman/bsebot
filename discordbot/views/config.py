import discord
from logging import Logger

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.config_admin import AdminConfigView
from discordbot.views.config_revolution import RevolutionConfigView
from discordbot.views.config_salary import SalaryConfigView
from discordbot.views.config_threads import ThreadConfigView
from discordbot.views.config_valorant import ValorantConfigView
from discordbot.views.config_wordle import WordleConfigView

from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.guilds import Guilds


class ConfigView(discord.ui.View):
    def __init__(
        self,
        logger: Logger = PlaceHolderLogger
    ):
        super().__init__(timeout=120)
        self.logger = logger
        self.spoiler_threads = SpoilerThreads()
        self.guilds = Guilds()
        self.config_select = ConfigSelect()
        self.add_item(self.config_select)

    def _check_perms(self, value: str, interaction: discord.Interaction) -> bool:
        """
        Checks if the user has the right perms to configure this item

        Args:
            value (str): the configurable item
            interaction (discord.Interaction): the interaction

        Returns:
            bool: whether they do or don't
        """

        # is option in options that allow normal users to use it
        if value in ["threads", ]:
            return True

        # is user the creator
        if interaction.user.id == CREATOR:
            return True

        # now we check server perms
        guild_db = self.guilds.get_guild(interaction.guild_id)

        # is user the server owner
        if interaction.user.id == guild_db["owner_id"]:
            return True

        # is user in server admins
        if interaction.user.id in guild_db.get("admins", []):
            return True

        return False

    async def _send_no_perms_message(self, interaction: discord.Interaction) -> None:
        """
        Sends a message stating they don't have perm

        Args:
            interaction (discord.Interaction): the interaction
        """
        msg = "You do not have the required permissions to configure this option."
        await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        value = self.config_select._selected_values[0]
        await interaction.response.edit_message(
            content="Loading your config option now...",
            view=None,
            delete_after=2
        )

        if not self._check_perms(value, interaction):
            self.logger.info(f"User {interaction.user} tried to configure {value} without the right perms")
            return await self._send_no_perms_message(interaction)

        match value:
            case "admins":
                msg, view = self._get_admins_message_and_view(interaction)
            case "revolution":
                msg, view = self._get_revolution_message_and_view(interaction)
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

        guild_db = self.guilds.get_guild(interaction.guild_id)
        admins = guild_db.get("admins", [])

        threads = []
        for thread in threads:
            if not thread.get("active"):
                continue
            if interaction.user.id == CREATOR:
                threads.append(thread)
                continue
            elif interaction.user.id in admins:
                threads.append(thread)
                continue
            elif interaction.user.id == thread.get("owner", thread.get("creator", CREATOR)):
                threads.append(thread)
                continue

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

    def _get_admins_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """
        Handle admin message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        admins = guild_db.get("admins", [])

        view = AdminConfigView()

        if not admins:
            _admins = "_None_"
        else:
            _admins = ", ".join([f"<@{a}>" for a in admins])

        msg = (
            "**Admins Config**\n\n"
            "Select the users that should be BSEBot Admins and be able to perform administrative functions. "
            "Select _all_ users you want to be admins - including existing ones if you wish for them "
            "to remain as admins.\n\n"
            f"Current admins: {_admins}\n\n"
            "**Note**: the server owner and the BSEBot creator are _always_ considered as admins regardless of your "
            "selection.\n"
        )
        return msg, view

    def _get_revolution_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle revolution message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        rev_enabled = guild_db.get("revolution", True)
        view = RevolutionConfigView(rev_enabled)
        msg = (
            "**Revolution Config**\n\n"
            "Select whether the revolution event is enabled or not."
        )
        return msg, view

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
