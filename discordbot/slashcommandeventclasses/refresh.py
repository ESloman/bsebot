
import discord

from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import BSEddiesCloseBet
from discordbot.slashcommandeventclasses.place import BSEddiesPlaceBet
from discordbot.views.refresh import RefreshBetView


class BSEddiesRefreshBet(BSEddies):
    """
    Class for handling `/refresh` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.bseddies_close = BSEddiesCloseBet(client, guilds, logger)
        self.bseddies_place = BSEddiesPlaceBet(client, guilds, logger)

    async def create_refresh_view(
            self,
            ctx: discord.ApplicationContext,
            bet_ids: list = None
    ) -> None:

        if not bet_ids:
            _ids = []
            bets = self.user_bets.get_all_inactive_pending_bets(ctx.guild_id)
            bets.extend(self.user_bets.get_all_pending_bets(ctx.guild_id))
            _bets = []
            for bet in bets:
                if bet.get("type"):
                    continue
                if bet["bet_id"] not in _ids:
                    _ids.append(bet["bet_id"])
                    _bets.append(bet)
            bet_ids = _bets

        if len(bet_ids) == 0:
            await ctx.respond(content="There are no active bets to bet on right now.", ephemeral=True)
            return

        refresh_bet_view = RefreshBetView(bet_ids, self.bseddies_place, self.bseddies_close)
        await ctx.respond(content="**Choose bet to refresh**", view=refresh_bet_view, ephemeral=True)
