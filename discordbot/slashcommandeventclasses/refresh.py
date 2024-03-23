"""Refresh slash command."""

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.views.refresh import RefreshBetView


class RefreshBet(BSEddies):
    """Class for handling `/refresh` commands."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs

        """
        super().__init__(client, guild_ids)
        self.bseddies_close = CloseBet(client, guild_ids)
        self.bseddies_place = PlaceBet(client, guild_ids)
        self.activity_type = ActivityTypes.REFRESH
        self.help_string = "Refresh a bet"
        self.command_name = "refresh"

    async def create_refresh_view(self, ctx: discord.ApplicationContext, bet_ids: list | None = None) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
            bet_ids (list | None): the bet IDs
        """
        if not bet_ids:
            _ids = []
            bets = self.user_bets.get_all_inactive_pending_bets(ctx.guild_id)
            bets.extend(self.user_bets.get_all_pending_bets(ctx.guild_id))
            _bets = []
            for bet in bets:
                if bet.bet_id not in _ids:
                    _ids.append(bet.bet_id)
                    _bets.append(bet)
            bet_ids = _bets

        if len(bet_ids) == 0:
            await ctx.respond(content="There are no active bets to bet on right now.", ephemeral=True, delete_after=10)
            return

        refresh_bet_view = RefreshBetView(bet_ids, self.bseddies_place, self.bseddies_close)
        await ctx.respond(content="**Choose bet to refresh**", view=refresh_bet_view, ephemeral=True)
