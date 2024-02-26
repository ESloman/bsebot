"""Refresh bet views."""

import discord

from discordbot.embedmanager import EmbedManager
from discordbot.selects.bet import BetSelect
from discordbot.views.bet import BetView
from discordbot.views.bseview import BSEView
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB


class RefreshBetView(BSEView):
    """Class for refresh bet view."""

    def __init__(self, bets: list[BetDB], place: callable, close: callable) -> None:
        """Initialisation method.

        Args:
            bets (list): the bet IDs
            place (callable): the place function
            close (callable): the close function
        """
        super().__init__(timeout=60)
        self.bets = UserBets()
        self.bseddies_place = place
        self.bseddies_close = close
        self.embed_manager = EmbedManager()
        self.bet_select = BetSelect(bets)
        self.add_item(self.bet_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True, emoji="💰")
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        try:
            bet_id = self.bet_select.values[0]
        except (IndexError, AttributeError, TypeError):
            # this means that this was default
            bet_id = self.bet_select.options[0].value

        bet = self.bets.get_bet_from_id(interaction.guild_id, bet_id)
        channel = await interaction.guild.fetch_channel(bet.channel_id)
        message = await channel.fetch_message(bet.message_id)
        embed = self.embed_manager.get_bet_embed(bet)
        content = f"# {bet.title}\n_Created by <@{bet.user}>_"
        view = BetView(bet, self.bseddies_place, self.bseddies_close)
        await message.edit(content=content, view=view, embed=embed)
        await interaction.response.edit_message(content="Refreshed the bet for you.", view=None, delete_after=2)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled.", view=None, delete_after=2)
