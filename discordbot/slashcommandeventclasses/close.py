
import datetime

import discord

import discordbot.views as views
from discordbot.betmanager import BetManager
from discordbot.bot_enums import TransactionTypes, ActivityTypes
from discordbot.slashcommandeventclasses import BSEddies


class BSEddiesCloseBet(BSEddies):
    """
    Class for handling `/bseddies bet close` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.bet_manager = BetManager(logger)

    async def create_bet_view(
            self,
            ctx: discord.ApplicationContext,
            bet_ids: list = None
    ) -> None:

        if not bet_ids:
            bet_ids = self.user_bets.query(
                {"closed": None, "guild_id": ctx.guild_id, "user": ctx.user.id},
                projection={"bet_id": True, "title": True, "created": True, "option_dict": True}
            )

        if len(bet_ids) == 0:
            try:
                await ctx.respond(content="You have no bets to close.", ephemeral=True)
            except AttributeError:
                await ctx.response.send_message(content="You have no bets to close.", ephemeral=True)
            return

        if len(bet_ids) > 25:
            bet_ids = sorted(bet_ids, key=lambda x: x["created"], reverse=True)
            bet_ids = bet_ids[:24]

        close_bet_view = views.CloseABetView(bet_ids, submit_callback=self.close_bet)
        try:
            await ctx.respond(content="**Closing a bet**", view=close_bet_view, ephemeral=True)
        except AttributeError:
            await ctx.response.send_message(content="**Closing a bet**", view=close_bet_view, ephemeral=True)

    async def close_bet(
            self,
            ctx: discord.Interaction,
            bet_id: str,
            emoji: str
        ) -> None:
        """
        This is the method for handling when we close a bet.

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
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_BET_CLOSE,
            bet_id=bet_id, emoji=emoji
        )

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        author = ctx.user

        if not bet:
            msg = f"This bet doesn't exist."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        if not bet["active"] and bet["result"] is not None:
            msg = f"You cannot close a bet that is already closed."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        if bet["user"] != author.id:
            msg = f"You cannot close a bet that isn't yours."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        emoji = emoji.strip()

        if emoji not in bet["option_dict"]:
            msg = f"{emoji} isn't a valid outcome so the bet can't be closed."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id)
            return

        # the logic in this if statement only applies if the user "won" their own bet and they were the only better
        # they just get refunded the eddies that put in
        if bet_dict := bet["betters"].get(str(author.id), None):
            if len(bet["betters"]) == 1 and bet_dict["emoji"] == emoji:

                self.logger.info(f"{ctx.user.id} just won a bet ({bet_id}) where they were the only better...")
                self.user_bets.close_a_bet(bet["_id"], emoji)
                self.user_points.increment_points(author.id, guild.id, bet_dict["points"])
                self.user_points.append_to_transaction_history(
                    ctx.user.id,
                    guild.id,
                    {
                        "type": TransactionTypes.BET_REFUND,
                        "amount": bet_dict["points"],
                        "timestamp": datetime.datetime.now(),
                        "bet_id": bet_id,
                        "comment": "User won their own bet when no-one else entered."
                    }
                )
                if not author.dm_channel:
                    await author.create_dm()
                try:
                    msg = (f"Looks like you were the only person to bet on your bet and you _happened_ to win it. "
                           f"As such, you have won **nothing**. However, you have been refunded the eddies that you "
                           f"originally bet.")
                    await author.send(content=msg)
                except discord.errors.Forbidden:
                    pass

                desc = (f"**{bet['title']}**\n\nThere were no winners on this bet. {author.mention} just _happened_ "
                        f"to win a bet they created and they were the only entry. They were refunded the amount of "
                        f"eddies that they originally bet.")
                # update the message to reflect that it's closed
                channel = guild.get_channel(bet["channel_id"])
                if not channel:
                    # channel is thread
                    channel = guild.get_thread(bet["channel_id"])

                message = channel.get_partial_message(bet["message_id"])
                await message.edit(content=desc, view=None, embeds=[])
                await ctx.followup.edit_message(content="Closed the bet for you!", view=None, message_id=ctx.message.id)
                return

        ret_dict = self.bet_manager.close_a_bet(bet_id, guild.id, emoji)

        desc = f"**{bet['title']}**\n{emoji} - **{ret_dict['outcome_name']['val']}** won!\n\n"

        for better in ret_dict["winners"]:
            desc += f"\n- {guild.get_member(int(better)).name} won `{ret_dict['winners'][better]}` eddies!"

        author = guild.get_member(ctx.user.id)

        # message the losers to tell them the bad news
        for loser in ret_dict["losers"]:
            mem = guild.get_member(int(loser))
            if not mem.dm_channel:
                await mem.create_dm()
            try:
                points_bet = ret_dict["losers"][loser]
                msg = (f"**{author.name}** just closed bet "
                       f"`[{bet_id}] - {bet['title']}` and the result was {emoji} "
                       f"(`{ret_dict['outcome_name']['val']})`.\n"
                       f"As this wasn't what you voted for - you have lost. You bet **{points_bet}** eddies.")
                await mem.send(content=msg)
            except discord.errors.Forbidden:
                pass

        # message the winners to tell them the good news
        for winner in ret_dict["winners"]:
            mem = guild.get_member(int(winner))
            if not mem.dm_channel:
                await mem.create_dm()
            try:
                msg = (f"**{author.name}** just closed bet "
                       f"`[{bet_id}] - {bet['title']}` and the result was {emoji} "
                       f"(`{ret_dict['outcome_name']['val']})`.\n"
                       f"**This means you won!!** "
                       f"You have won `{ret_dict['winners'][winner]}` BSEDDIES!!")
                await mem.send(content=msg)
            except discord.errors.Forbidden:
                pass

        # update the message to reflect that it's closed
        channel = guild.get_channel(bet["channel_id"])
        if not channel:
            # channel is thread
            channel = guild.get_thread(bet["channel_id"])
        message = channel.get_partial_message(bet["message_id"])

        await message.edit(content=desc, view=None, embeds=[])
        await ctx.followup.edit_message(content="Closed the bet for you!", view=None, message_id=ctx.message.id)

    async def cancel_bet(
            self,
            ctx: discord.Interaction,
            bet_id: str
        ) -> None:
        """
        This is the method for handling when we close a bet.

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
            ctx.user, ctx.guild_id, ActivityTypes.BSEDDIES_BET_CANCEL,
            bet_id=bet_id
        )

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        author = ctx.user

        if not bet:
            msg = f"This bet doesn't exist."
            await ctx.followup.edit_message(content=msg, view=None, message_id=ctx.message.id, embeds=[])
            return

        if not bet["active"] and bet["result"] is not None:
            msg = f"You cannot cancel a bet that is already closed."
            await ctx.followup.send(content=msg, view=None, ephemeral=True)
            await ctx.followup.edit_message(view=None, message_id=ctx.message.id, embeds=[])
            return

        if bet["user"] != author.id:
            msg = f"You cannot cancel a bet that isn't yours."
            await ctx.followup.send(content=msg, view=None, ephemeral=True)
            return

        if betters := bet.get("betters"):
            for better in betters:
                bet_dict = betters[better]
                self.user_points.increment_points(int(better), guild.id, bet_dict["points"])
                self.user_points.append_to_transaction_history(
                    int(better),
                    guild.id,
                    {
                        "type": TransactionTypes.BET_REFUND,
                        "amount": bet_dict["points"],
                        "timestamp": datetime.datetime.now(),
                        "bet_id": bet_id,
                        "comment": "Bet was cancelled."
                    }
                )

        self.user_bets.close_a_bet(bet["_id"], "cancelled")
        # update the message to reflect that it's closed
        channel = guild.get_channel(bet["channel_id"])
        if not channel:
            # channel is thread
            channel = guild.get_thread(bet["channel_id"])
        message = channel.get_partial_message(bet["message_id"])
        await message.edit(content="Bet has been cancelled. Any bets were refunded to the betters.", view=None, embeds=[])
