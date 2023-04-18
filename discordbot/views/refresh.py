
import discord
from discordbot.embedmanager import EmbedManager
from discordbot.selects.bet import BetSelect
from discordbot.views.bet import BetView
from mongo.bsepoints.bets import UserBets


class RefreshBetView(discord.ui.View):
    def __init__(self, bet_ids: list, place: callable, close: callable):
        super().__init__(timeout=60)
        self.bets = UserBets()
        self.bseddies_place = place
        self.bseddies_close = close
        self.embed_manager = EmbedManager()
        self.add_item(BetSelect(bet_ids))

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="This `refresh` command timed out - please _place_ another one", view=None)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True, emoji="💰")
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        for child in self.children:
            if type(child) == BetSelect:
                try:
                    bet_id = child.values[0]
                except IndexError:
                    # this means that this was default
                    bet_id = child.options[0].value
                break

        bet = self.bets.get_bet_from_id(interaction.guild_id, bet_id)
        channel = await interaction.guild.fetch_channel(bet["channel_id"])
        message = await channel.fetch_message(bet["message_id"])
        embed = self.embed_manager.get_bet_embed(interaction.guild, bet_id, bet)
        content = (
            f"# {bet['title']}\n"
            f"_Created by <@{bet['user']}>_"
        )
        view = BetView(bet, self.bseddies_place, self.bseddies_close)
        await message.edit(content=content, view=view, embed=embed)
        await interaction.response.edit_message(content="Refreshed the bet for you.", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)
