"""Views for config activities."""

import discord

from discordbot.modals.activities import ActivityModal
from discordbot.selects.activitiesconfig import ActivityTypeSelect
from discordbot.views.bseview import BSEView
from mongo.bsedataclasses import BotActivities


class ActivityConfigView(BSEView):
    """Class for activity config view."""

    def __init__(self) -> None:
        """Initialisation method."""
        super().__init__(timeout=120)

        self.activity_select = ActivityTypeSelect()
        self.add_item(self.activity_select)

    async def update(self, interaction: discord.Interaction) -> None:
        """View update method.

        Can be called by child types when something changes.

        Args:
            interaction (discord.Interaction): _description_
        """
        selected = self.activity_select.values

        self.toggle_button(not bool(selected), "Next")

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        selected = self.get_select_value(self.activity_select)

        match selected:
            case "listening":
                placeholder_text = "Listening to..."
            case "watching":
                placeholder_text = "Watching..."
            case "playing":
                placeholder_text = "Playing..."
            case _:
                placeholder_text = "???"

        modal = ActivityModal(selected, placeholder_text)
        await interaction.response.send_modal(modal)
        await interaction.followup.delete_message(interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)


class ActivityConfirmView(BSEView):
    """Class for activity config view."""

    def __init__(self, activity_type: str, placeholder: str, name: list[str]) -> None:
        """Initialisation method.

        Args:
            activity_type (str): the activity type
            placeholder (str): the placeholder text
            name (list[str]): the name of the activities
        """
        super().__init__(timeout=120)
        self.activity_type = activity_type
        self.placeholder = placeholder
        self.name = name
        self.bot_activities = BotActivities()

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=False)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        _already_existed = []
        for activity in self.name:
            existing = self.bot_activities.find_activity(activity, self.activity_type)

            if existing:
                _already_existed.append(activity)
                continue

            self.bot_activities.insert_activity(self.activity_type, activity, interaction.user.id)

        if len(_already_existed) == len(self.name):
            # all our options existed already
            await interaction.response.edit_message(
                content="All your options already existed - nothing has changed.",
                view=None,
                delete_after=3,
            )
            return

        content = f"Submitted your activit{"y" if len(self.name) == 1 else "ies"} to the database."
        if _already_existed:
            content += f" These, (`{_already_existed}`) existed already and weren't added again."

        await interaction.response.edit_message(content=content, view=None, delete_after=4)

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, row=4, disabled=False)
    async def edit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        modal = ActivityModal(self.activity_type, self.placeholder, self.name)
        await interaction.response.send_modal(modal)
        await interaction.followup.delete_message(interaction.message.id)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
