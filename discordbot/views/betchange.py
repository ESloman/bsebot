
import discord

import discordbot.views.bet
from discordbot.embedmanager import EmbedManager
from discordbot.selects.betoutcomes import BetOutcomesSelect
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet

from mongo.bsepoints.bets import UserBets
from mongo.datatypes import Bet


class BetChange(discord.ui.View):
    def __init__(
        self,
        bet: Bet,
        place: PlaceBet,
        close: CloseBet
    ):
        super().__init__(timeout=None)
        self.bet: Bet = bet
        self.user_bets = UserBets()
        self.embed_manager = EmbedManager()

        self.place = place
        self.close = close

        outcomes = bet["option_dict"]
        options = [
            discord.SelectOption(
                label=outcomes[key]["val"],
                value=key,
                emoji=key
            ) for key in outcomes
        ]

        self.outcome_select = BetOutcomesSelect(options, discord.ui.Button)
        self.add_item(self.outcome_select)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:

        await interaction.response.defer(ephemeral=True)

        value = self.outcome_select.values[0]

        self.bet["betters"][str(interaction.user.id)]["emoji"] = value

        self.user_bets.update(
            {"_id": self.bet["_id"]},
            {"$set": {f"betters.{interaction.user.id}.emoji": value}}
        )

        # refresh view for users
        bet = self.user_bets.get_bet_from_id(interaction.guild_id, self.bet["bet_id"])
        channel = await interaction.guild.fetch_channel(bet["channel_id"])
        message = await channel.fetch_message(bet["message_id"])
        embed = self.embed_manager.get_bet_embed(interaction.guild, bet["bet_id"], bet)
        view = discordbot.views.bet.BetView(bet, self.place, self.close)
        await message.edit(embed=embed, view=view)
        await interaction.followup.edit_message(
            message_id=interaction.message.id,
            content="Updated your bet for you.",
            view=None
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, disabled=False, emoji="✖️")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None, ephemeral=True, delete_after=2)
