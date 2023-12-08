"""Refresh bet views."""

import contextlib

import discord

from discordbot.embedmanager import EmbedManager
from discordbot.selects.bet import BetSelect
from discordbot.views.bet import BetView
from mongo.bsepoints.bets import UserBets


class RefreshBetView(discord.ui.View):
    """Class for refresh bet view."""

    def __init__(self, bet_ids: list, place: callable, close: callable) -> None:
        """Initialisation method.

        Args:
            bet_ids (list): the bet IDs
            place (callable): the place function
            close (callable): the close function
        """
        super().__init__(timeout=60)
        self.bets = UserBets()
        self.bseddies_place = place
        self.bseddies_close = close
        self.embed_manager = EmbedManager()
        self.add_item(BetSelect(bet_ids))

    async def on_timeout(self) -> None:
        """View timeout function.

        Is invoked when the message times out.
        """
        for child in self.children:
            child.disabled = True

        with contextlib.suppress(discord.NotFound, AttributeError):
            # not found is when the message has already been deleted
            # don't need to edit in that case
            await self.message.edit(content="This `refresh` command timed out - please _place_ another one", view=None)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True, emoji="💰")
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        for child in self.children:
            if type(child) is BetSelect:
                try:
                    bet_id = child.values[0]
                except (IndexError, AttributeError):
                    # this means that this was default
                    bet_id = child.options[0].value
                break

        bet = self.bets.get_bet_from_id(interaction.guild_id, bet_id)
        channel = await interaction.guild.fetch_channel(bet["channel_id"])
        message = await channel.fetch_message(bet["message_id"])
        embed = self.embed_manager.get_bet_embed(interaction.guild, bet)
        content = f"# {bet['title']}\n_Created by <@{bet['user']}>_"
        view = BetView(bet, self.bseddies_place, self.bseddies_close)
        await message.edit(content=content, view=view, embed=embed)
        await interaction.response.edit_message(content="Refreshed the bet for you.", view=None)

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, delete_after=2)
