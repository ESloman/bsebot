import discord

from discordbot.selects.wordleconfig import WordleEmojiSelect

from mongo.bsepoints.emojis import ServerEmojis
from mongo.bsepoints.guilds import Guilds


class WordleEmojiReactionConfigView(discord.ui.View):
    def __init__(
        self,
        guild_id
    ):
        super().__init__(timeout=120)
        self.guilds = Guilds()
        self.emojis = ServerEmojis()

        guild_db = self.guilds.get_guild(guild_id)
        emoji_list = self.emojis.get_all_emojis(guild_id)

        current_x = guild_db.get("wordle_x_emoji")
        current_two = guild_db.get("wordle_two_emoji")
        current_six = guild_db.get("wordle_six_emoji")

        self.x_select = WordleEmojiSelect(emoji_list, "X", current_x)
        self.two_select = WordleEmojiSelect(emoji_list, "2", current_two)
        self.six_select = WordleEmojiSelect(emoji_list, "6", current_six)

        self.add_item(self.x_select)
        self.add_item(self.two_select)
        self.add_item(self.six_select)

    async def update(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content=interaction.message.content, view=self)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=4)
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        x_val = None
        try:
            x_val = self.x_select.values[0]
        except IndexError:
            for opt in self.x_select.options:
                if opt.default:
                    x_val = opt.value
                    break

        two_val = None
        try:
            two_val = self.two_select.values[0]
        except IndexError:
            for opt in self.two_select.options:
                if opt.default:
                    two_val = opt.value
                    break

        six_val = None
        try:
            six_val = self.six_select.values[0]
        except IndexError:
            for opt in self.six_select.options:
                if opt.default:
                    six_val = opt.value
                    break

        self.guilds.update(
            {"guild_id": interaction.guild.id},
            {
                "$set": {
                    "wordle_x_emoji": x_val,
                    "wordle_two_emoji": two_val,
                    "wordle_six_emoji": six_val
                }
            }
        )

        await interaction.response.edit_message(
            content="Wordle reaction emojis updated.",
            view=None,
            delete_after=5
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️", row=4)
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="Cancelled", view=None)
