import discord

from discordbot.modals.activities import ActivityModal
from discordbot.selects.activitiesconfig import ActivityTypeSelect

from mongo.bsedataclasses import BotActivities


class ActivityConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

        self.activity_select = ActivityTypeSelect()
        self.add_item(self.activity_select)

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        try:
            await self.message.edit(content="This timed out - please _place_ another one", view=None)
        except (discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            pass

    async def update(self, interaction: discord.Interaction):

        selected = self.activity_select.values

        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Next":
                child.disabled = not bool(selected)
                break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            selected = self.activity_select.values[0]
        except IndexError:
            # look for default as user didn't select one explicitly
            for opt in self.activity_select.options:
                if opt.default:
                    selected = opt.value
                    break

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

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)


class ActivityConfirmView(discord.ui.View):
    def __init__(self, activity_type: str, placeholder: str, name: str):
        super().__init__(timeout=120)
        self.activity_type = activity_type
        self.placeholder = placeholder
        self.name = name
        self.bot_activities = BotActivities()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True

        try:
            await self.message.edit(content="This timed out - please _place_ another one", view=None)
        except (discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            pass

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=False)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        existing = self.bot_activities.find_activity(self.name, self.activity_type)

        if existing:
            # already exists
            await interaction.response.edit_message(
                content="Your activity already exists - no changes were made.",
                view=None,
                delete_after=5
            )
            return

        self.bot_activities.insert_activity(self.activity_type, self.name, interaction.user.id)

        await interaction.response.edit_message(
            content="Submitted your activity to the database.",
            view=None,
            delete_after=2
        )

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.gray, row=4, disabled=False)
    async def edit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        modal = ActivityModal(self.activity_type, self.placeholder, self.name)
        await interaction.response.send_modal(modal)
        await interaction.followup.delete_message(interaction.message.id)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
