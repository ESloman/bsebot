
import discord

from discordbot.modals.autogenerate import AddCategory, AddBet
from discordbot.selects.autogenerateconfig import AutogenerateConfigSelect, AutogenerateCategorySelect

from mongo.bsepoints.guilds import Guilds


class AutoGenerateConfigView(discord.ui.View):
    def __init__(
        self
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()

        self.auto_config = AutogenerateConfigSelect()
        self.category_select = AutogenerateCategorySelect()

        self.add_item(self.auto_config)

    async def update(self, interaction: discord.Interaction):

        try:
            auto_val = self.auto_config.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    auto_val = opt.value
                    break

        cat_val = None
        try:
            cat_val = self.category_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    cat_val = opt.value
                    break

        if auto_val in ["category", ]:
            # remove category select as we don't need it
            try:
                if len(self.children) > 3:
                    self.remove_item(self.category_select)
            except Exception:
                pass

            for child in self.children:
                if type(child) is discord.ui.Button and child.label == "Submit":
                    child.disabled = False
                    break

        elif auto_val in ["new", ]:
            # add category select
            if len(self.children) < 4:
                self.add_item(self.category_select)

            for child in self.children:
                if type(child) is discord.ui.Button and child.label == "Submit":
                    child.disabled = not bool(cat_val)
                    break

        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4, disabled=True)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        try:
            auto_val = self.auto_config.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    auto_val = opt.value
                    break

        cat_val = None
        try:
            cat_val = self.category_select.values[0]
        except (IndexError, AttributeError):
            for opt in self.auto_config.options:
                if opt.default:
                    cat_val = opt.value
                    break

        if auto_val == "category":
            modal = AddCategory()
            await interaction.response.send_modal(modal)
        elif auto_val == "new":
            modal = AddBet(cat_val)
            await interaction.response.send_modal(modal)

        await interaction.followup.delete_message(
            message_id=interaction.message.id
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
