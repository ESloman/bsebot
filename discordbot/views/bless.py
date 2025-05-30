"""Bless views."""

import discord

from discordbot.bot_enums import ActivityTypes, SupporterType, TransactionTypes
from discordbot.selects.bless import BlessAmountSelect, BlessClassSelect
from discordbot.views.bseview import BSEView
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class BlessView(BSEView):
    """Class for Bless view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=None)
        self.amount_select = BlessAmountSelect()
        self.class_select = BlessClassSelect()
        self.add_item(self.class_select)
        self.add_item(self.amount_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()
        self.activities = UserActivities()

    @discord.ui.button(label="Bless", style=discord.ButtonStyle.blurple, emoji="📈", row=2)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        value = self.get_select_value(self.amount_select)
        value = int(value) if value else 100

        class_value = self.get_select_value(self.class_select)

        self.activities.add_activity(
            interaction.user.id,
            interaction.guild.id,
            ActivityTypes.BLESS_ACTUAL,
            value=value,
            class_value=class_value,
        )

        if not value or not class_value:
            msg = "Please select who should be blessed and how much by."
            await interaction.response.edit_message(content=msg, view=None)
            return

        user_db = self.user_points.find_user(interaction.user.id, interaction.guild.id)
        points = user_db.points
        if points < value:
            msg = "Not enough eddies to give out this many."
            await interaction.response.edit_message(content=msg, view=None)
            return

        # get the user list
        _users = self.user_points.get_all_users_for_guild(interaction.guild.id)

        if class_value == "all":
            users = [u for u in _users if u.daily_minimum and not u.king]
        else:
            users = [
                u for u in _users if u.daily_minimum and not u.king and u.supporter_type == SupporterType.SUPPORTER
            ]

        num_users = len(users)

        if not num_users:
            msg = "There are 0 users that match the criteria. No eddies were distributed."
            await interaction.response.edit_message(content=msg, view=None)
            return

        eddies_each = round(value / num_users)
        eddies_given = 0
        for user in users:
            self.user_points.increment_points(
                user.uid,
                interaction.guild.id,
                eddies_each,
                TransactionTypes.BLESS_RECEIVE,
            )
            eddies_given += eddies_each

        self.user_points.increment_points(
            interaction.user.id,
            interaction.guild.id,
            eddies_given * -1,
            TransactionTypes.BLESS_GIVE,
        )

        msg = (
            f"Successfully bless `{num_users}` with `{eddies_each}` eddies each. "
            f"You were substracted `{eddies_given}` eddies."
        )
        await interaction.response.edit_message(content=msg, view=None)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None)
