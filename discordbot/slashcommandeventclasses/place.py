"""Place slash command."""

import logging

import discord

import discordbot.views.bet
from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.views.place import PlaceABetView


class PlaceBet(BSEddies):
    """Class for handling `/bseddies bet place` commands."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.bseddies_close = CloseBet(client, guild_ids, logger)
        self.activity_type = ActivityTypes.BSEDDIES_BET_PLACE
        self.help_string = "Place eddies on a bet"
        self.command_name = "place"

    async def create_bet_view(
        self,
        ctx: discord.ApplicationContext | discord.Interaction,
        bet_ids: list | None = None,
    ) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
            bet_ids (list | None): the bet IDs
        """
        if not bet_ids:
            bet_ids = self.user_bets.query(
                {"active": True, "guild_id": ctx.guild_id},
                projection={"bet_id": True, "title": True, "option_dict": True},
            )

        if len(bet_ids) == 0:
            try:
                await ctx.respond(content="There are no active bets to bet on right now.", ephemeral=True)
            except AttributeError:
                await ctx.response.send_message(content="There are no active bets to bet on right now.", ephemeral=True)
            return

        points = self.user_points.get_user_points(ctx.user.id, ctx.guild_id)

        place_bet_view = PlaceABetView(bet_ids, points, submit_callback=self.place_bet)
        try:
            await ctx.respond(content="**Placing a bet**", view=place_bet_view, ephemeral=True)
        except AttributeError:
            await ctx.response.send_message(content="**Placing a bet**", view=place_bet_view, ephemeral=True)

    async def place_bet(  # noqa: PLR0911
        self,
        ctx: discord.Interaction,
        bet_id: str,
        amount: int,
        emoji: str,
    ) -> None | bool:
        """Main method for placing a bet.

        Validates that a bet exists, is active and that the user has the right amount of BSEddies.
        It also checks that the bet being placed is either new, or the same as the existing bet the user
        has for this bet.

        Args:
            ctx (discord.Interaction): _description_
            bet_id (str): _description_
            amount (int): _description_
            emoji (str): _description_

        Returns:
            None | bool: _description_
        """
        if not await self._handle_validation(ctx):
            return None

        self._add_event_type_to_activity_history(
            ctx.user,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_BET_PLACE,
            bet_id=bet_id,
            amount=amount,
            emoji=emoji,
        )

        response = ctx.response  # type: discord.InteractionResponse

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

        if not bet:
            msg = "This bet doesn't exist."
            await response.edit_message(content=msg, view=None, delete_after=10)
            return None

        view = discordbot.views.bet.BetView(bet, self, self.bseddies_close)

        if not bet["active"]:
            msg = f"Your reaction on **Bet {bet_id}** failed as the bet is closed for new bets."
            await response.edit_message(content=msg, view=None, delete_after=10)
            return None

        emoji = emoji.strip()

        if emoji not in bet["option_dict"]:
            msg = f"Your reaction on **Bet {bet_id}** failed as that reaction isn't a valid outcome."
            await response.edit_message(content=msg, view=None, delete_after=10)
            return None

        if amount <= 0:
            msg = "Cannot bet negative eddies or 0 eddies."
            await response.edit_message(content=msg, view=None, delete_after=10)
            return None

        success = self.user_bets.add_better_to_bet(bet_id, guild.id, ctx.user.id, emoji, amount)

        if not success["success"]:
            msg = f"Your bet on **Bet {bet_id}** failed cos __{success['reason']}__?"
            await response.edit_message(content=msg, view=None, delete_after=10)
            return False

        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        channel = await self.client.fetch_channel(bet["channel_id"])

        if not channel:
            # channel is thread
            channel = guild.get_thread(bet["channel_id"])

        message = channel.get_partial_message(bet["message_id"])
        embed = self.embed_manager.get_bet_embed(guild, bet_id, bet)
        content = f"# {bet['title']}\n_Created by <@{bet['user']}>_"
        await message.edit(content=content, embed=embed, view=view)
        await response.edit_message(content="Placed the bet for you!", view=None, delete_after=10)
        return None
