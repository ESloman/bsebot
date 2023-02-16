import datetime

import discord

from discordbot.bot_enums import ActivityTypes, SupporterType
from discordbot.selects.bless import BlessAmountSelect, BlessClassSelect

from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class BlessView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.amount_select = BlessAmountSelect()
        self.class_select = BlessClassSelect()
        self.add_item(self.class_select)
        self.add_item(self.amount_select)
        self.guilds = Guilds()
        self.user_points = UserPoints()

    def _append_to_history(self, user_id, guild_id, _type: ActivityTypes, **params):

        doc = {
            "type": _type,
            "timestamp": datetime.datetime.now(),
        }
        if params:
            doc["comment"] = f"Command parameters: {', '.join([f'{key}: {params[key]}' for key in params])}"

        doc["value"] = params["value"]
        self.user_points.append_to_activity_history(user_id, guild_id, doc)

    @discord.ui.button(label="Bless", style=discord.ButtonStyle.blurple, emoji="📈", row=2)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        try:
            value = int(self.amount_select.values[0])
        except (IndexError, AttributeError):
            value = int([o for o in self.amount_select.options if o.default][0].value)

        class_value = [o for o in self.class_select.options if o.default][0].value

        self._append_to_history(
            interaction.user.id, interaction.guild.id, ActivityTypes.BLESS_ACTUAL, value=value,
            class_value=class_value
        )

        if not value or not class_value:
            msg = "Please select who should be blessed and how much by."
            await interaction.response.edit_message(
                content=msg,
                view=None
            )
            return

        user_db = self.user_points.find_user(interaction.user.id, interaction.guild.id)
        points = user_db["points"]
        if points < value:
            msg = "Not enough eddies to give out this many."
            await interaction.response.edit_message(
                content=msg,
                view=None
            )
            return

        # get the user list
        _users = self.user_points.get_all_users_for_guild(interaction.guild.id)

        if class_value == "all":
            users = [u for u in _users if u.get("daily_minimum", 0) and not u.get("king", False)]
        else:
            users = [
                u for u in _users
                if u.get("daily_minimum", 0) and
                not u.get("king", False) and
                u.get("supporter_type", 0) == SupporterType.SUPPORTER
            ]

        num_users = len(users)

        if not num_users:
            msg = "There are 0 users that match the criteria. No eddies were distributed."
            await interaction.response.edit_message(
                content=msg,
                view=None
            )
            return

        eddies_each = round(value / num_users)
        eddies_given = 0
        for user in users:
            self.user_points.increment_points(
                user["uid"], interaction.guild.id, eddies_each
            )
            eddies_given += eddies_each

        self.user_points.decrement_points(
            interaction.user.id, interaction.guild.id, eddies_given
        )

        msg = (
            f"Successfully bless `{num_users}` with `{eddies_each}` eddies each. "
            f"You were substracted `{eddies_given}` eddies."
        )
        await interaction.response.edit_message(
            content=msg,
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray, emoji="✖️", row=2)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
