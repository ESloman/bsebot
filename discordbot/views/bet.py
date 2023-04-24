
import discord

from discordbot.modals.addoption import AddBetOption
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet

from mongo.bsepoints.bets import UserBets
from mongo.datatypes import Bet


class BetView(discord.ui.View):
    def __init__(
        self,
        bet: Bet,
        bseddies_place: PlaceBet,
        bseddies_close: CloseBet
    ):
        super().__init__(timeout=None)
        self.bet: Bet = bet
        self.place: PlaceBet = bseddies_place
        self.close: CloseBet = bseddies_close
        self.user_bets = UserBets()

    @discord.ui.button(label="Place a bet", style=discord.ButtonStyle.blurple, emoji="💰")
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.place.create_bet_view(interaction, [self.bet, ])

    @discord.ui.button(label="Close this bet", style=discord.ButtonStyle.gray)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.close.create_bet_view(interaction, [self.bet, ])

    @discord.ui.button(label="Add option", style=discord.ButtonStyle.gray)
    async def add_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        if interaction.user.id != self.bet["user"]:
            message = "You weren't the bet creator - you can't do this."
            await interaction.response.send_message(content=message, ephemeral=True, delete_after=10)
            return

        _bet = self.user_bets.get_bet_from_id(self.bet["guild_id"], self.bet["bet_id"])

        if not _bet["active"] or _bet.get("closed", False):
            message = "Bet isn't available to add more options."
            await interaction.response.send_message(content=message, ephemeral=True, delete_after=10)
            return

        option_modal = AddBetOption(_bet, self.place, self.close)
        await interaction.response.send_modal(option_modal)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.close.cancel_bet(interaction, self.bet["bet_id"])
