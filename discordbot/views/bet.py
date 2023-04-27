
import datetime

import discord

from discordbot.modals.addoption import AddBetOption
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.views.betchange import BetChange

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

    @discord.ui.button(label="Change your bet", style=discord.ButtonStyle.gray)
    async def change_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        _bet = self.user_bets.get_bet_from_id(self.bet["guild_id"], self.bet["bet_id"])

        if interaction.user.id not in _bet["users"]:
            message = "You can't change your bet for a bet you haven't bet on yet."
            await interaction.response.send_message(content=message, ephemeral=True, delete_after=10)
            return

        _bet = self.user_bets.get_bet_from_id(self.bet["guild_id"], self.bet["bet_id"])

        if not _bet["active"] or _bet.get("closed", False):
            message = "Bet is closed - you can't change your bet."
            await interaction.response.send_message(content=message, ephemeral=True, delete_after=10)
            return

        first_bet_time = _bet["betters"][str(interaction.user.id)]["first_bet"]
        now = datetime.datetime.now()
        if (now - first_bet_time).seconds > 300 and (now - _bet.get("updated", _bet["created"])).seconds > 300:
            message = "It's been too long since your original bet - you can't change it now."
            await interaction.response.send_message(content=message, ephemeral=True, delete_after=10)
            return

        _view = BetChange(_bet, self.place, self.close)
        await interaction.response.send_message(content="Select another bet option.", view=_view, ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.close.cancel_bet(interaction, self.bet["bet_id"])
