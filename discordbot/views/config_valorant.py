import discord
from bson import Int64

from discordbot.selects.valorantconfig import ValorantActiveSelect, ValorantChannelSelect, ValorantRoleSelect
from mongo.bsepoints.guilds import Guilds


class ValorantConfigView(discord.ui.View):
    def __init__(
        self,
        guild_id
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()

        guild_db = self.guilds.get_guild(guild_id)
        active = "1" if guild_db.get("valorant_rollcall") else "0"

        self.active_select = ValorantActiveSelect(active)
        self.channel_select = ValorantChannelSelect()
        self.role_select = ValorantRoleSelect()

        if int(active):
            self.channel_select.disabled = False
            self.role_select.disabled = False

        self.add_item(self.active_select)
        self.add_item(self.channel_select)
        self.add_item(self.role_select)

    async def update(self, interaction: discord.Interaction):

        try:
            active_val = self.active_select.values[0]
        except IndexError:
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        self.channel_select.disabled = not active_val
        self.role_select.disabled = not active_val

        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Submit":
                break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        guild_db = self.guilds.get_guild(interaction.guild_id)

        try:
            active_val = bool(int(self.active_select.values[0]))
        except IndexError:
            for opt in self.active_select.options:
                if opt.default:
                    active_val = bool(int(opt.value))
                    break

        channel = guild_db.get("valorant_channel")
        try:
            channel = self.channel_select.values[0]
        except (AttributeError, IndexError):
            for opt in self.channel_select.options:
                if opt.default:
                    channel = opt.value
                    break

        if channel and type(channel) not in [int, Int64]:
            channel = channel.id

        role = guild_db.get("valorant_role")
        try:
            role = self.role_select.values[0]
        except (AttributeError, IndexError):
            for opt in self.role_select.options:
                if opt.default:
                    role = opt.value
                    break

        if role and type(role) not in [int, Int64]:
            role = role.id

        self.guilds.set_valorant_config(interaction.guild_id, active_val, channel, role)

        await interaction.response.edit_message(
            content="Valorant config updated.",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
