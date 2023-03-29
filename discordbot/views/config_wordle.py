import discord
from bson import Int64

from discordbot.selects.wordleconfig import WordleActiveSelect, WordleChannelSelect, WordleReminderSelect

from mongo.bsepoints.guilds import Guilds


class WordleConfigView(discord.ui.View):
    def __init__(
        self,
        guild_id
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()

        guild_db = self.guilds.get_guild(guild_id)
        active = "1" if guild_db.get("wordle") else "0"

        self.active_select = WordleActiveSelect(active)
        self.channel_select = WordleChannelSelect()

        if int(active):
            self.channel_select.disabled = False

        reminder = "1" if guild_db.get("wordle_reminders") else "0"
        self.reminder_select = WordleReminderSelect(reminder)

        self.add_item(self.active_select)
        self.add_item(self.channel_select)
        self.add_item(self.reminder_select)

    async def update(self, interaction: discord.Interaction):

        try:
            active_val = self.active_select.values[0]
        except IndexError:
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        self.channel_select.disabled = not active_val
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            active_val = bool(int(self.active_select.values[0]))
        except IndexError:
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        channel = None
        try:
            channel = self.channel_select.values[0]
        except IndexError:
            for opt in self.channel_select.options:
                if opt.default:
                    channel = opt.value
                    break

        if channel and type(channel) not in [int, Int64]:
            channel = channel.id

        try:
            reminders = bool(int(self.reminder_select.values[0]))
        except IndexError:
            for opt in self.reminder_select.options:
                if opt.default:
                    reminders = bool(int(opt.value))
                    break

        self.guilds.set_wordle_config(interaction.guild_id, active_val, channel, reminders)

        await interaction.response.edit_message(
            content="Wordle config updated.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
