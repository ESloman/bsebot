"""Close slash command."""

import logging

import discord

from discordbot.betmanager import BetManager
from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.views.close import CloseABetView
from mongo.datatypes.bet import BetDB


class CloseBet(BSEddies):
    """Class for handling `/bseddies bet close` commands."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.bet_manager = BetManager(logger)
        self.activity_type = ActivityTypes.BSEDDIES_BET_CLOSE
        self.help_string = "Resolves an existing bet"
        self.command_name = "close"

    async def create_bet_view(self, ctx: discord.ApplicationContext, bets: list[BetDB] | None = None) -> None:
        """Creates the view.

        Args:
            ctx (discord.ApplicationContext): the context
            bets (list[Bet] | None): the list of bets. Defaults to None.
        """
        if not bets:
            bets = [
                bet for bet in self.user_bets.get_all_inactive_pending_bets(ctx.guild_id) if bet.user == ctx.user.id
            ]

        if len(bets) == 0:
            try:
                await ctx.respond(content="You have no bets to close.", ephemeral=True, delete_after=10)
            except AttributeError:
                await ctx.response.send_message(content="You have no bets to close.", ephemeral=True, delete_after=10)
            return

        if len(bets) > 25:  # noqa: PLR2004
            bets = sorted(bets, key=lambda x: x.created, reverse=True)
            bets = bets[:24]

        close_bet_view = CloseABetView(bets, submit_callback=self.close_bet)
        try:
            await ctx.respond(content="**Closing a bet**", view=close_bet_view, ephemeral=True)
        except AttributeError:
            await ctx.response.send_message(content="**Closing a bet**", view=close_bet_view, ephemeral=True)

    async def close_bet(self, ctx: discord.Interaction, bet_id: str, emoji: list[str]) -> None:  # noqa: C901, PLR0912, PLR0915
        """This is the method for handling when we close a bet.

        We validate that the user initiating the command is the user who created the bet and that
        the bet is still open in the first place. We also make sure that the result the user
        provided us is actually a valid result for the bet.

        If that's all okay - we close the bet and dish out the BSEddies to the winners.
        We also inform the winners/losers what the result was and how many BSEddies they won (if any).

        Args:
            ctx (discord.Interaction): slash command context
            bet_id (str): the BET ID
            emoji (str): the winning outcome emoji
        :return: None
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.response.defer()

        self._add_event_type_to_activity_history(
            ctx.user,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_BET_CLOSE,
            bet_id=bet_id,
            emoji=emoji,
        )

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        author = ctx.user

        if not bet:
            msg = "This bet doesn't exist."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        if not bet.active and bet.result is not None:
            msg = "You cannot close a bet that is already closed."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        if bet.user != author.id:
            msg = "You cannot close a bet that isn't yours."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        for _emoji in emoji:
            stripped_emoji = _emoji.strip()
            if stripped_emoji not in bet.option_dict:
                msg = f"{stripped_emoji} isn't a valid outcome so the bet can't be closed."
                await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
                return

        # the logic in this if statement only applies if the user "won" their own bet and they were the only better
        # they just get refunded the eddies that put in
        bet_dict = bet.betters.get(str(author.id), None)
        if bet_dict and len(bet.betters) == 1 and bet_dict.emoji in emoji:
            self.logger.info("%s just won a bet (%s) where they were the only better...", ctx.user.id, bet_id)
            self.user_bets.close_a_bet(bet._id, emoji)  # noqa: SLF001
            self.user_points.increment_points(
                author.id,
                guild.id,
                bet_dict.points,
                TransactionTypes.BET_REFUND,
                comment="User won their own bet when no-one else entered.",
                bet_id=bet_id,
            )
            if not author.dm_channel:
                await author.create_dm()
            try:
                msg = (
                    "Looks like you were the only person to bet on your bet and you _happened_ to win it. "
                    "As such, you have won **nothing**. However, you have been refunded the eddies that you "
                    "originally bet."
                )
                await author.send(content=msg, silent=True)
            except discord.Forbidden:
                pass

            desc = (
                f"**{bet.title}**\n\nThere were no winners on this bet. {author.mention} just _happened_ "
                f"to win a bet they created and they were the only entry. They were refunded the amount of "
                f"eddies that they originally bet."
            )
            # update the message to reflect that it's closed
            channel = await self.client.fetch_channel(bet.channel_id)

            message = channel.get_partial_message(bet.message_id)
            await message.edit(content=desc, view=None, embeds=[])
            await ctx.followup.edit_message(content="Closed the bet for you!", view=None, message_id=ctx.message.id)
            return

        ret_dict = self.bet_manager.close_a_bet(bet_id, guild.id, emoji)

        desc = f"# {bet.title}\nBet ID: {bet_id}\n"

        outcomes = ""
        for result in zip(ret_dict["result"], ret_dict["outcome_name"], strict=True):
            outcomes += f"\n- {result[0]} {result[1].val}"

        desc += f"\nWinning outcome(s):{outcomes}"
        desc += "\n## Winners"

        for better in ret_dict["winners"]:
            desc += f"\n- {guild.get_member(int(better)).name} won `{ret_dict['winners'][better]}` eddies!"

        if not ret_dict["winners"]:
            desc += "\n- There were no winners 😦"

        desc += f"\n\nThe **KING** (<@{ret_dict['king']}>) gained _{ret_dict['king_tax']}_ eddies from tax."

        author = guild.get_member(ctx.user.id)
        if not author:
            author = await guild.fetch_member(ctx.user.id)

        # get the message reference here so we can link it in DMs
        # update the message to reflect that it's closed
        channel = await self.client.fetch_channel(bet.channel_id)
        message = channel.get_partial_message(bet.message_id)

        # message the losers to tell them the bad news
        for loser in ret_dict["losers"]:
            mem = guild.get_member(int(loser))
            if not mem.dm_channel:
                await mem.create_dm()
            try:
                points_bet = ret_dict["losers"][loser]
                msg = (
                    f"**{author.name}** just closed bet "
                    f"`[{bet_id}]` - [{bet.title}](<{message.jump_url}>) and the result was {emoji} "
                    f"(`{', '.join([n.val for n in ret_dict['outcome_name']])})`.\n"
                    f"As this wasn't what you voted for - you have lost. You bet **{points_bet}** eddies."
                )
                await mem.send(content=msg, silent=True)
            except discord.Forbidden:
                pass

        # message the winners to tell them the good news
        for winner in ret_dict["winners"]:
            mem = guild.get_member(int(winner))
            if not mem.dm_channel:
                await mem.create_dm()
            try:
                msg = (
                    f"**{author.name}** just closed bet "
                    f"`[{bet_id}]` - [{bet.title}](<{message.jump_url}>) and the result was {emoji} "
                    f"(`{', '.join([n['val'] for n in ret_dict['outcome_name']])})`.\n"
                    f"**This means you won!!** "
                    f"You have won `{ret_dict['winners'][winner]}` BSEDDIES!!"
                )
                await mem.send(content=msg, silent=True)
            except discord.Forbidden:
                pass

        await message.edit(content=desc, view=None, embeds=[])
        await ctx.followup.edit_message(content="Closed the bet for you!", view=None, message_id=ctx.message.id)

    async def cancel_bet(self, ctx: discord.Interaction, bet_id: str) -> None:
        """This is the method for handling when we close a bet.

        We validate that the user initiating the command is the user who created the bet and that
        the bet is still open in the first place. We also make sure that the result the user
        provided us is actually a valid result for the bet.

        If that's all okay - we close the bet and dish out the BSEddies to the winners.
        We also inform the winners/losers what the result was and how many BSEddies they won (if any).

        :param ctx: slash command context
        :param bet_id: str - the BET ID
        :param emoji: str - the winning outcome emoji
        :return: None
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.response.defer()

        self._add_event_type_to_activity_history(
            ctx.user,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_BET_CANCEL,
            bet_id=bet_id,
        )

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        author = ctx.user

        if not bet:
            msg = "This bet doesn't exist."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id, embeds=[])
            return

        if not bet.active and bet.result is not None:
            msg = "You cannot cancel a bet that is already closed."
            await ctx.followup.send(content=msg, ephemeral=True, delete_after=10)
            await ctx.followup.edit_message(view=None, message_id=ctx.message.id, embeds=[])
            return

        if bet.user != author.id:
            msg = "You cannot cancel a bet that isn't yours."
            await ctx.followup.send(content=msg, ephemeral=True, delete_after=10)
            return

        if betters := bet.betters:
            for better in betters:
                bet_dict = betters[better]
                self.user_points.increment_points(
                    int(better),
                    guild.id,
                    bet_dict.points,
                    TransactionTypes.BET_REFUND,
                    comment="Bet was cancelled",
                    bet_id=bet_id,
                )

        self.user_bets.close_a_bet(bet._id, "cancelled")  # noqa: SLF001
        # update the message to reflect that it's closed
        channel = await self.client.fetch_channel(bet.channel_id)
        message = channel.get_partial_message(bet.message_id)
        await message.edit(
            content="Bet has been cancelled. Any bets were refunded to the betters.",
            view=None,
            embeds=[],
        )
