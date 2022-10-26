
import discord

import discordbot.slashcommandeventclasses as slashcommandeventclasses


class BetView(discord.ui.View):
    def __init__(
        self,
        bet: dict,
        bseddies_place: slashcommandeventclasses.BSEddiesPlaceBet,
        bseddies_close: slashcommandeventclasses.BSEddiesCloseBet
    ):
        super().__init__(timeout=None)
        self.bet = bet
        self.place = bseddies_place
        self.close = bseddies_close

    @discord.ui.button(label="Place a bet", style=discord.ButtonStyle.blurple, emoji="💰")
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.place.create_bet_view(interaction, [self.bet, ])

    @discord.ui.button(label="Close this bet", style=discord.ButtonStyle.gray)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.close.create_bet_view(interaction, [self.bet, ])
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, emoji="✖️")
    async def cancel_ballback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        await self.close.cancel_bet(interaction, self.bet["bet_id"])
