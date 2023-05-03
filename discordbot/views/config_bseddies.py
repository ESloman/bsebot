import discord
from bson import Int64

from discordbot.selects.bseddiesconfig import BSEddiesChannelSelect, BSEddiesRoleSelect
from mongo.bsepoints.guilds import Guilds


class BSEddiesConfigView(discord.ui.View):
    def __init__(
        self
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.channel_select = BSEddiesChannelSelect()
        self.king_select = BSEddiesRoleSelect("KING")
        self.supporter_select = BSEddiesRoleSelect("Supporter Faction")
        self.revolutionary_select = BSEddiesRoleSelect("Revolutionary Faction")

        self.add_item(self.channel_select)
        self.add_item(self.king_select)
        self.add_item(self.supporter_select)
        self.add_item(self.revolutionary_select)

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        channel = None
        try:
            channel = self.channel_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.channel_select.options:
                if opt.default:
                    channel = opt.value
                    break

        if channel and type(channel) not in [int, Int64]:
            channel = channel.id

        king_role = None
        try:
            king_role = self.king_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.king_select.options:
                if opt.default:
                    king_role = opt.value

        if king_role and type(king_role) not in [int, Int64]:
            king_role = king_role.id

        supporter_role = None
        try:
            supporter_role = self.supporter_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.supporter_select.options:
                if opt.default:
                    supporter_role = opt.value

        if supporter_role and type(supporter_role) not in [int, Int64]:
            supporter_role = supporter_role.id

        revolutionary_role = None
        try:
            revolutionary_role = self.revolutionary_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.revolutionary_select.options:
                if opt.default:
                    revolutionary_role = opt.value

        if revolutionary_role and type(revolutionary_role) not in [int, Int64]:
            revolutionary_role = revolutionary_role.id

        update_dict = {}

        if channel:
            update_dict["channel"] = channel
        if king_role:
            update_dict["role"] = king_role
        if revolutionary_role:
            update_dict["revolutionary_role"] = revolutionary_role
        if supporter_role:
            update_dict["supporter_role"] = supporter_role

        if update_dict:
            self.guilds.update({"guild_id": interaction.guild_id}, {"$set": update_dict})

        await interaction.response.edit_message(
            content="BSEddies config updated.",
            view=None,
            delete_after=5
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
