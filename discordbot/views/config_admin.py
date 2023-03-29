import discord

from discordbot.selects.adminconfig import AdminUserSelect

from mongo.bsepoints.guilds import Guilds


class AdminConfigView(discord.ui.View):
    def __init__(
        self
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.admins_select = AdminUserSelect()
        self.add_item(self.admins_select)

    async def update(self, interaction: discord.Interaction):

        selected = self.admins_select.values

        for child in self.children:
            if type(child) == discord.ui.Button and child.label == "Submit":
                child.disabled = not bool(selected)
                break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        selected = self.admins_select.values

        user_ids = [user.id for user in selected]

        self.guilds.update(
            {"guild_id": interaction.guild_id},
            {"$set": {"admins": user_ids}}
        )

        admins = ", ".join([f"<@{a}>" for a in user_ids])

        await interaction.response.edit_message(
            content=f"Admins updated. New admins: {admins}",
            view=None,
            delete_after=10
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
