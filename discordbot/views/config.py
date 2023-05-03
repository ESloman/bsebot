
import datetime
from logging import Logger

import discord

from discordbot.constants import CREATOR
from discordbot.selects.config import ConfigSelect
from discordbot.utilities import PlaceHolderLogger
from discordbot.views.config_admin import AdminConfigView
from discordbot.views.config_autogenerate import AutoGenerateConfigView
from discordbot.views.config_bseddies import BSEddiesConfigView
from discordbot.views.config_revolution import RevolutionConfigView
from discordbot.views.config_salary import SalaryConfigView
from discordbot.views.config_salary_message import DailyMessageView
from discordbot.views.config_threads import ThreadConfigView
from discordbot.views.config_valorant import ValorantConfigView
from discordbot.views.config_wordle import WordleConfigView
from discordbot.views.config_wordle_reactions import WordleEmojiReactionConfigView

from mongo.bsedataclasses import SpoilerThreads
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.datatypes import GuildDB


class ConfigView(discord.ui.View):
    def __init__(
        self,
        logger: Logger = PlaceHolderLogger,
        user_id: int = None,
        guild_id: int = None
    ):
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
            for value in ConfigSelect._values:
                if self._check_perms(value[1], user_id, guild_db=guild_db):
                    configurable_items.append(value)

        self.config_select = ConfigSelect(configurable_items)
        self.add_item(self.config_select)

    def _check_perms(
        self,
        value: str,
        user_id: int,
        guild_id: int = None,
        guild_db: GuildDB = None
    ) -> bool:
        """
        Checks if the user has the right perms to configure this item

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
            if value in ["daily_salary", ]:
                return True
            return False

        # is option in options that allow normal users to use it
        if value in ["threads", "daily_salary"]:
            return True

        # is user the creator
        if user_id == CREATOR:
            return True

        # now we check server perms
        if not guild_db:
            guild_db = self.guilds.get_guild(guild_id)

        # is user the server owner
        if user_id == guild_db["owner_id"]:
            return True

        # is user in server admins
        if user_id in guild_db.get("admins", []):
            return True

        return False

    async def _send_no_perms_message(self, interaction: discord.Interaction) -> None:
        """
        Sends a message stating they don't have perm

        Args:
            interaction (discord.Interaction): the interaction
        """
        msg = "You do not have the required permissions to configure this option."
        await interaction.followup.send(msg, ephemeral=True, delete_after=10)

    @discord.ui.button(label="Select", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        value = self.config_select._selected_values[0]
        await interaction.response.edit_message(
            content="Loading your config option now...",
            view=None,
            delete_after=2
        )

        guild_id = interaction.guild.id if interaction.guild else None

        if not self._check_perms(value, interaction.user.id, guild_id):
            self.logger.info(f"User {interaction.user} tried to configure {value} without the right perms")
            return await self._send_no_perms_message(interaction)

        match value:
            case "admins":
                msg, view = self._get_admins_message_and_view(interaction)
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
            case "wordle_reactions":
                msg, view = self._get_wordle_reaction_message_and_view(interaction)
            case _:
                # default case
                msg = "unknown"
                view = None

        try:
            await interaction.followup.send(msg, ephemeral=True, view=view)
        except AttributeError:
            await interaction.followup.send(msg, ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=2)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)

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

        now = datetime.datetime.now()

        configurable_threads = []
        for thread in threads:
            if not thread.get("active") and (now - thread["created"]).days >= 30:
                # only exclude non-active ones if they're super old
                continue
            if interaction.user.id == CREATOR:
                configurable_threads.append(thread)
                continue
            elif interaction.user.id in admins:
                configurable_threads.append(thread)
                continue
            elif interaction.user.id == thread.get("owner", thread.get("creator", CREATOR)):
                configurable_threads.append(thread)
                continue

        if not configurable_threads:
            view = None
            msg = "No available threads for you to configure."

        else:
            view = ThreadConfigView(configurable_threads)
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

    def _get_daily_salary_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """
        Handle daily salary message message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        if interaction.guild:
            user = self.user_points.find_user(interaction.user.id, interaction.guild.id)
            daily_eddies = user["daily_eddies"]
            daily_summary = user.get("daily_summary", False)
        else:
            users = self.user_points.query({"uid": interaction.user.id})
            daily_eddies = False
            daily_summary = False
            for user in users:
                if user["daily_eddies"]:
                    daily_eddies = True
                if user.get("daily_summary", False):
                    daily_summary = True

        is_admin = self._check_perms("salary_summary", interaction.user.id, interaction.guild.id)

        view = DailyMessageView(daily_eddies, is_admin, daily_summary)
        msg = (
            "# Daily Salary Message\n\n"
            "Select whether you want to receive the _(silent)_ daily salary message or not."
        )

        if is_admin:
            msg += (
                "\nThen select if you would like to receive the daily salary summary (everyone else's eddies) or not."
            )

        return msg, view

    def _get_wordle_reaction_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle wordle reaction message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        view = WordleEmojiReactionConfigView(interaction.guild_id)
        msg = (
            "**Wordle Emoji Reaction Config**\n\n"
            "Select which server emojis the bot uses to react to different Wordle scores.\n"
            "If None are selected, the defaults will be used.\n\n"
            "1.) X score\n"
            "2.) 2 score\n"
            "6.) 6 score\n"
        )
        return msg, view

    def _get_bseddies_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle bseddies message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """
        guild_db = self.guilds.get_guild(interaction.guild_id)
        _chan = guild_db.get("channel")
        king_role = guild_db.get("role")
        supporter_role = guild_db.get("supporter_role")
        revolutionary_role = guild_db.get("revolutionary_role")
        chan_mention = f"<#{_chan}>" if _chan else "_None_"
        king_mention = f"<@&{king_role}>" if king_role else "_None_"
        supp_mention = f"<@&{supporter_role}>" if supporter_role else "_None_"
        rev_mention = f"<@&{revolutionary_role}>" if revolutionary_role else "_None_"

        view = BSEddiesConfigView()
        msg = (
            "**BSEddies Config**\n\n"
            "The bot needs, at a minimum, a 'BSEddies channel' to post most messages to and a 'KING' role that "
            "the user with the most eddies will receive. Ideally, this role is moved high up in the role "
            "hierarchy so that it's visible to everyone. The 'BSEBot' role will need to higher than it so that "
            "it can reassign as necessary. It is also recommended to set a 'Supporter' and 'Revolutionary' role "
            "to denote these 'factions'.\n\n"
            "Select the following options:\n"
            f"1.) The BSEddies channel (current: {chan_mention})\n"
            f"2.) The KING role (current: {king_mention})\n"
            f"3.) The Supporter role (current: {supp_mention})\n"
            f"4.) The Revolutionary role (current: {rev_mention})\n\n"
            "Leaving any of these blank will keep the current options."
        )
        return msg, view

    def _get_autogenerate_message_and_view(self, interaction: discord.Interaction) -> tuple[str, discord.ui.View]:
        """Handle autogenerate message/view

        Args:
            interaction (discord.Interaction): the interaction

        Returns:
            tuple[str, discord.ui.View]: the message and view
        """

        view = AutoGenerateConfigView()
        msg = (
            "**Autogenerate Config**\n\n"
            "What would you like to do?"
        )
        return msg, view
