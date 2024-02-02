"""Bet Change view."""

from typing import TYPE_CHECKING

import discord

from discordbot.embedmanager import EmbedManager
from discordbot.selects.betoutcomes import BetOutcomesSelect
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.close import CloseBet
    from discordbot.slashcommandeventclasses.place import PlaceBet
    from discordbot.views.bet import BetView


class BetChange(discord.ui.View):
    """Class for bet change view."""

    def __init__(self, bet: BetDB, view: "BetView", place: "PlaceBet", close: "CloseBet") -> None:
        """Initialisation method.

        Args:
            bet (Bet): the bet
            view (BetView): the view
            bseddies_place (PlaceBet): the place class
            bseddies_close (CloseBet): the close class
        """
        super().__init__(timeout=None)
        self.bet: BetDB = bet
        self.view: "BetView" = view
        self.user_bets = UserBets()
        self.embed_manager = EmbedManager()

        self.place = place
        self.close = close

        outcomes = bet.option_dict
        options = [discord.SelectOption(label=outcomes[key].val, value=key, emoji=key) for key in outcomes]

        self.outcome_select = BetOutcomesSelect(options, discord.ui.Button)
        self.add_item(self.outcome_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2)
    async def submit_callback(self, _: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.defer(ephemeral=True)

        value = self.outcome_select.values[0]

        self.user_bets.update(
            {"_id": self.bet._id},  # noqa: SLF001
            {"$set": {f"betters.{interaction.user.id}.emoji": value}},
        )

        # refresh view for users
        bet = self.user_bets.get_bet_from_id(interaction.guild_id, self.bet.bet_id)
        channel = await interaction.guild.fetch_channel(bet.channel_id)
        message = await channel.fetch_message(bet.message_id)
        embed = self.embed_manager.get_bet_embed(interaction.guild, bet)
        self.view.bet = bet
        await message.edit(embed=embed, view=self.view)
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            content="Updated your bet for you.",
            view=None,
        )

    @staticmethod
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, disabled=False, emoji="✖️")
    async def cancel_callback(_: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Button callback.

        Args:
            _ (discord.ui.Button): the button pressed
            interaction (discord.Interaction): the callback interaction
        """
        await interaction.response.edit_message(content="Cancelled", view=None, ephemeral=True, delete_after=2)
