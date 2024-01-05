"""Config views."""

import datetime
from logging import Logger

import discord

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.selects.wordleconfig import WordleRootSelect
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.config_activities import ActivityConfigView
from discordbot.views.config_admin import AdminConfigView
from discordbot.views.config_autogenerate import AutoGenerateConfigView
from discordbot.views.config_bseddies import BSEddiesConfigView
from discordbot.views.config_revolution import RevolutionConfigView
from discordbot.views.config_salary import SalaryConfigView
from discordbot.views.config_salary_message import DailyMessageView
from discordbot.views.config_threads import ThreadConfigView
from discordbot.views.config_valorant import ValorantConfigView
from discordbot.views.config_wordle import WordleRootConfigView
from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.datatypes import GuildDB


class ConfigView(discord.ui.View):
    """Class for config view."""

    def __init__(
        self, logger: Logger = PlaceHolderLogger, user_id: int | None = None, guild_id: int | None = None
    ) -> None:
        """Initialisation method.

        Args:
            logger (Logger, optional): the logger. Defaults to PlaceHolderLogger.
            user_id (int | None, optional): the user ID. Defaults to None.
            guild_id (int | None, optional): the guild ID. Defaults to None.
        """
        super().__init__(timeout=120)
        self.logger = logger
        self.spoiler_threads = SpoilerThreads()
        self.guilds = Guilds()
        self.user_points = UserPoints()

        # build a list of configurable items to show the user
        # don't show the user options they can't actually configure
        # reduces complexity somewhat
        configurable_items = []
        if user_id:
            guild_db = self.guilds.get_guild(guild_id) if guild_id else None
            configurable_items.extend(
                value
                for value in ConfigSelect._values  # noqa: SLF001
                if self._check_perms(value[1], user_id, guild_db=guild_db)
            )

        self.config_select = ConfigSelect(configurable_items)
        self.add_item(self.config_select)

    def _check_perms(self, value: str, user_id: int, guild_id: int | None = None, guild_db: GuildDB = None) -> bool:  # noqa: PLR0911
        """Checks if the user has the right perms to configure this item.

        Args:
            value (str): the configurable item
            user_id (int): the user ID
            guild_id (int): guild ID
            guild_db (GuildDB): guild dict

        Returns:
            bool: whether they do or don't
        """
        # check we have a guild
        if not guild_id and not guild_db:
            # no guild specified - these are the non-guild options that can be configured
            if value == "daily_salary":
                return True
            return False

        # is option in options that allow normal users to use it
        if value in {"activities", "threads", "daily_salary", "wordle_reminders"}:
            return True

        # is user the creator
        if user_id == CREATOR:
            return True

        # creator only configuration options
        if value == "wordle_starting_words" and user_id != CREATOR:
            return False

        # now we check server perms
        if not guild_db:
            guild_db = self.guilds.get_guild(guild_id)

        # is user the server owner
        if user_id == guild_db.owner_id:
            return True

        # is user in server admins
        if user_id in guild_db.admins:
            return True

        return False

    @staticmethod
    async def _send_no_perms_message(interaction: discord.Interaction) -> None:
        """Sends a message stating they don't have perm.

        Args:
            interaction (discord.Interaction): the interaction
        """
        msg = "You do not have the required permissions to configure this option."
        await interaction.followup.send(msg, ephemeral=True, delete_after=10)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        value = self.config_select._selected_values[0]  # noqa: SLF001

        if value != "wordle_reminders":
            await interaction.response.edit_message(
                content="Loading your config option now...",
                view=None,
                delete_after=2,
            )

        guild_id = interaction.guild.id if interaction.guild else None

        if not self._check_perms(value, interaction.user.id, guild_id):
            self.logger.info("User %s tried to configure %s without the right perms", interaction.user, value)
            return await self._send_no_perms_message(interaction)

        match value:
            case "admins":
                msg, view = self._get_admins_message_and_view(interaction)
            case "activities":
                msg, view = self._get_activities_message_and_view(interaction)
            case "autogenerate":
                msg, view = self._get_autogenerate_message_and_view(interaction)
            case "bseddies":
                msg, view = self._get_bseddies_message_and_view(interaction)
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
            case "daily_salary":
                msg, view = self._get_daily_salary_message_and_view(interaction)
            case _:
                # default case
                msg = "unknown"
                view = None

        try:
            await interaction.followup.send(msg, ephemeral=True, view=view)
        except AttributeError:
            await interaction.followup.send(msg, ephemeral=True)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)

    def _get_thread_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle thread message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        threads = self.spoiler_threads.get_all_threads(interaction.guild_id)

        guild_db = self.guilds.get_guild(interaction.guild_id)
        admins = guild_db.admins

        now = datetime.datetime.now()

        configurable_threads = []
        for thread in threads:
            if not thread.active and (now - thread.created).days >= 30:  # noqa: PLR2004
                # only exclude non-active ones if they're super old
                continue

            if (
                interaction.user.id == CREATOR
                or interaction.user.id in admins
                or interaction.user.id == (thread.owner or thread.creator)
            ):
                configurable_threads.append(thread)

        if not configurable_threads:
            view = None
            msg = "No available threads for you to configure."

        else:
            view = ThreadConfigView(configurable_threads)
            msg = (
                "## Thread Configuration\n"
                "Select a thread to configure, and then select whether it should send mute reminders and "
                "on _which_ day.\n\n"
            )

        return msg, view

    def _get_valorant_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle valorant message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _chan = guild_db.valorant_channel
        _role = guild_db.valorant_role
        chan_mention = f"<#{_chan}>" if _chan else "_None_"
        role_mention = f"<@&{_role}>" if _role else "_None_"
        view = ValorantConfigView(interaction.guild_id)

        msg = (
            "## Valorant Config\n\n"
            "Select the following options:\n"
            "- Whether to enable the daily vally rollcall\n"
            f"- If the above is true, which channel should the message be posted in? (Current: {chan_mention})\n"
            f"- Which role should be tagged in the message? (Current: {role_mention}).\n\n"
            "You can leave channel and role select blank to keep current values."
        )
        return msg, view

    def _get_daily_minimum_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle daily minimum message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _min = guild_db.daily_minimum or 4
        view = SalaryConfigView(_min)
        msg = (
            "## Salary Config\n\n"
            "Select the daily minimum salary for users in this guild. This amount is deprecated by one each day for "
            "each user that doesn't interact with the guild. This is reset for the user upon interaction.\n\n"
        )
        return msg, view

    def _get_admins_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle admin message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        admins = guild_db.admins

        view = AdminConfigView()

        _admins = "_None_" if not admins else ", ".join([f"<@{a}>" for a in admins])

        msg = (
            "## Admins Config\n\n"
            "Select the users that should be BSEBot Admins and be able to perform administrative functions. "
            "Select _all_ users you want to be admins - including existing ones if you wish for them "
            "to remain as admins.\n\n"
            f"Current admins: {_admins}\n\n"
            "**Note**: the server owner and the BSEBot creator are _always_ considered as admins regardless of your "
            "selection.\n"
        )
        return msg, view

    def _get_revolution_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle revolution message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        rev_enabled = guild_db.revolution if guild_db.revolution is not None else True
        view = RevolutionConfigView(rev_enabled)
        msg = "## Revolution Config\n\nSelect whether the revolution event is enabled or not."
        return msg, view

    def _get_daily_salary_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle daily salary message message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        if interaction.guild:
            user = self.user_points.find_user(interaction.user.id, interaction.guild.id)
            daily_eddies = user.daily_eddies
            daily_summary = user.daily_summary
        else:
            users = self.user_points.find_user_guildless(interaction.user.id)
            daily_eddies = False
            daily_summary = False
            for user in users:
                if user.daily_eddies:
                    daily_eddies = True
                if user.daily_summary:
                    daily_summary = True

        is_admin = self._check_perms("salary_summary", interaction.user.id, interaction.guild.id)

        view = DailyMessageView(daily_eddies, is_admin, daily_summary)
        msg = (
            "## Daily Salary Message\n\n"
            "Select whether you want to receive the _(silent)_ daily salary message or not."
        )

        if is_admin:
            msg += (
                "\nThen select if you would like to receive the daily salary summary (everyone else's eddies) or not."
            )

        return msg, view

    def _get_bseddies_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle bseddies message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _chan = guild_db.channel
        king_role = guild_db.role
        supporter_role = guild_db.supporter_role
        revolutionary_role = guild_db.revolutionary_role
        chan_mention = f"<#{_chan}>" if _chan else "_None_"
        king_mention = f"<@&{king_role}>" if king_role else "_None_"
        supp_mention = f"<@&{supporter_role}>" if supporter_role else "_None_"
        rev_mention = f"<@&{revolutionary_role}>" if revolutionary_role else "_None_"

        view = BSEddiesConfigView()
        msg = (
            "## BSEddies Config \n\n"
            "The bot needs, at a minimum, a 'BSEddies channel' to post most messages to and a 'KING' role that "
            "the user with the most eddies will receive. Ideally, this role is moved high up in the role "
            "hierarchy so that it's visible to everyone. The 'BSEBot' role will need to higher than it so that "
            "it can reassign as necessary. It is also recommended to set a 'Supporter' and 'Revolutionary' role "
            "to denote these 'factions'.\n\n"
            "Select the following options:\n"
            f"- The BSEddies channel (current: {chan_mention})\n"
            f"- The KING role (current: {king_mention})\n"
            f"- The Supporter role (current: {supp_mention})\n"
            f"- The Revolutionary role (current: {rev_mention})\n\n"
            "Leaving any of these blank will keep the current options."
        )
        return msg, view

    @staticmethod
    def _get_autogenerate_message_and_view(_: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle autogenerate message/view.

        Args:
            _ (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        view = AutoGenerateConfigView()
        msg = "## Autogenerate Config\n\nWhat would you like to do?"
        return msg, view

    @staticmethod
    def _get_activities_message_and_view(_: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle activities message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        view = ActivityConfigView()
        msg = "## Add an Activity\n\nSelect the type of activity you'd like."
        return msg, view

    def _get_wordle_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle wordle message/view.

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        _opts = [
            opt
            for opt in WordleRootSelect.selectable_options
            if self._check_perms(opt, interaction.user.id, interaction.guild_id)
        ]

        view = WordleRootConfigView(_opts)
        msg = "## Wordle Config\n\nSlect what you would like to configure."
        return msg, view
