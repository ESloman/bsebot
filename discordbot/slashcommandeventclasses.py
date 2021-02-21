import copy
import datetime
import math
import re

import discord
import discord_slash

from discordbot.clienteventclasses import BaseEvent
from discordbot.constants import BETA_USERS, CREATOR, PRIVATE_CHANNEL_IDS
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets, UserPoints


class BSEddies(BaseEvent):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def _handle_validation(self, ctx: discord_slash.context.SlashContext, **kwargs):
        """
        Internal method for validating slash command inputs.
        :param ctx:
        :return:
        """
        if ctx.guild.id not in self.guild_ids:
            return False

        if "friend" in kwargs and isinstance(kwargs["friend"], discord.User):
            if kwargs["friend"].bot:
                msg = f"Bots cannot be gifted eddies."
                await ctx.send(content=msg, hidden=True)
                return False

            if kwargs["friend"].id == ctx.author.id:
                msg = f"You can't gift yourself points."
                await ctx.send(content=msg, hidden=True)
                return False

        if "amount" in kwargs and isinstance(kwargs["amount"], int):
            if kwargs["amount"] < 0:
                msg = f"You can't _\"gift\"_ someone negative points."
                await ctx.send(content=msg, hidden=True)
                return False

        return True


class BSEddiesView(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def view(self, ctx):
        """
        Basic view method for handling view slash commands.
        If validation passes - it will inform the user of their current Eddies total.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
        pending = self.user_bets.get_user_pending_points(ctx.author.id, ctx.guild.id)
        msg = (f"You have **{points}** :money_with_wings:`BSEDDIES`:money_with_wings:!"
               f"\nAdditionally, you have `{pending}` points on 'pending bets'.")
        await ctx.send(content=msg, hidden=True)


class BSEddiesLeaderboard(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def leaderboard(self, ctx):
        """
        Basic method for sending the leaderboard to the channel that it was requested in.
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        embed = self.embed_manager.get_leaderboard_embed(ctx.guild, 5)
        message = await ctx.channel.send(content=embed)
        await message.add_reaction(u"▶️")


class BSEddiesActive(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def active(self, ctx: discord_slash.context.SlashContext):
        """
        Simple method for listing all the
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        bets = self.user_bets.get_all_pending_bets(ctx.guild.id)

        message = "Here are all the active bets:\n"

        for bet in bets:
            if 'channel_id' not in bet or 'message_id' not in bet:
                continue

            if bet.get("private"):
                if bet["channel_id"] != ctx.channel_id:
                    continue

            link = f"https://discordapp.com/channels/{ctx.guild.id}/{bet['channel_id']}/{bet['message_id']}"

            add_text = "OPEN FOR NEW BETS" if bet.get("active") else "CLOSED - AWAITING RESULT"

            pt = f"**{bets.index(bet) + 1})** [{bet['bet_id']} - `{add_text}`] _{bet['title']}_\n{link}\n\n"
            message += pt

        if len(bets) == 0:
            message = "There are no active bets :("

        await ctx.send(content=message)


class BSEddiesPending(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def pending(self, ctx: discord_slash.context.SlashContext):
        """
        Simple method for listing all the pending bets for a given user_id
        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        bets = self.user_bets.get_all_pending_bets_for_user(ctx.author.id, ctx.guild.id)

        message = "Here are all your pending bets:\n"

        for bet in bets:
            if 'channel_id' not in bet or 'message_id' not in bet:
                continue

            link = f"https://discordapp.com/channels/{ctx.guild.id}/{bet['channel_id']}/{bet['message_id']}"

            add_text = "OPEN FOR NEW BETS" if bet.get("active") else "CLOSED - AWAITING RESULT"

            pt = (f"**{bets.index(bet) + 1})** [{bet['bet_id']} - `{add_text}`] _{bet['title']}_"
                  f"\nOutcome: {bet['betters'][str(ctx.author.id)]['emoji']}\n"
                  f"Points: **{bet['betters'][str(ctx.author.id)]['points']}**\n{link}\n\n")
            message += pt

        if len(bets) == 0:
            message = "You have no pending bets :("

        self.logger.info(message)

        await ctx.send(content=message, hidden=True)


class BSEddiesGift(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def gift_eddies(self, ctx: discord_slash.context.SlashContext,
                          friend: discord.User,
                          amount: int):
        """
        Function for handling a 'gift eddies' event.

        We make sure that the user initiating the command has enough BSEddies to give to a friend
        and then we simply increment their friend's BSEddies and decrement theirs.

        :param ctx:
        :param friend:
        :param amount:
        :return:
        """
        if not await self._handle_validation(ctx, friend=friend, amount=amount):
            return

        points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
        if points < amount:
            msg = f"You have insufficient points to perform that action."
            await ctx.send(content=msg, hidden=True)
            return

        if not friend.dm_channel:
            await friend.create_dm()
        try:
            msg = f"**{ctx.author.name}** just gifted you `{amount}` eddies!!"
            await friend.send(content=msg)
        except discord.errors.Forbidden:
            pass

        self.user_points.decrement_points(ctx.author.id, ctx.guild.id, amount)
        self.user_points.increment_points(friend.id, ctx.guild.id, amount)

        await ctx.send(content=f"Eddies transferred to `{friend.name}`!", hidden=True)


class BSEddiesCloseBet(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def close_bet(
            self,
            ctx: discord_slash.context.SlashContext,
            bet_id: str,
            emoji: str,):
        """
        This is the method for handling when we close a bet.

        We validate that the user initiating the command is the user who created the bet and that
        the bet is still open in the first place. We also make sure that the result the user
        provided us is actually a valid result for the bet.

        If that's all okay - we close the bet and dish out the BSEddies to the winners.
        We also inform the winners/losers what the result was and how many BSEddies they won (if any).

        :param ctx:
        :param bet_id:
        :param emoji:
        :return:
        """

        if not await self._handle_validation(ctx):
            return

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

        if not bet:
            msg = f"This bet doesn't exist."
            await ctx.send(content=msg, hidden=True)
            return

        if not bet["active"] and bet["result"] is not None:
            msg = f"You cannot close a bet that is already closed."
            await ctx.send(content=msg, hidden=True)
            return

        if bet["user"] != ctx.author.id:
            msg = f"You cannot close a bet that isn't yours."
            await ctx.send(content=msg, hidden=True)
            return

        emoji = emoji.strip()

        if emoji not in bet["option_dict"]:
            msg = f"{emoji} isn't a valid outcome so the bet can't be closed."
            await ctx.send(content=msg, hidden=True)
            return

        ret_dict = self.user_bets.close_a_bet(bet_id, guild.id, emoji)

        desc = f"**{bet['title']}**\n{emoji} - **{ret_dict['outcome_name']['val']}** won!\n\n"

        for better in ret_dict["winners"]:
            desc += f"\n- {guild.get_member(int(better)).name} won `{ret_dict['winners'][better]}` eddies!"

        author = guild.get_member(ctx.author.id)

        # message the losers to tell them the bad news
        for loser in ret_dict["losers"]:
            mem = guild.get_member(int(loser))
            if not mem.dm_channel:
                await mem.create_dm()
            try:
                msg = (f"**{author.name}** just closed bet "
                       f"`[{bet_id}] - {bet['title']}` and the result was {emoji}.\n"
                       f"As this wasn't what you voted for - you have lost.")
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
                       f"`[{bet_id}] - {bet['title']}` and the result was {emoji}.\n"
                       f"**This means you won!!** "
                       f"You have won `{ret_dict['winners'][winner]}` BSEDDIES!!")
                await mem.send(content=msg)
            except discord.errors.Forbidden:
                pass

        # update the message to reflect that it's closed
        channel = guild.get_channel(bet["channel_id"])
        message = channel.get_partial_message(bet["message_id"])
        await message.edit(content=desc, embed=None)


class BSEddiesCreateBet(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)
        self.default_two_options = {"1️⃣": {"val": "succeed"}, "2️⃣": {"val": "fail"}}
        self.multiple_options_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

    async def handle_bet_creation(
            self,
            ctx: discord_slash.context.SlashContext,
            bet_title: str,
            option_one_name=None,
            option_two_name=None,
            option_three_name=None,
            option_four_name=None,
            timeout_str=None
    ):
        """
        The method that handles bet creation.

        We work out which outcome names we're gonna need - either custom or defaults.
        We make sure the user provided the right timeout or outcomes names (if at all).
        We then set the timeout for the bet.
        And we also work out which outcome emojis to use based of of the number of provided outcomes.

        Then we create the bet and send a message to channel the bet was created in.

        :param ctx:
        :param bet_title:
        :param option_one_name:
        :param option_two_name:
        :param option_three_name:
        :param option_four_name:
        :param timeout_str:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        points = self.user_points.get_user_points(ctx.author.id, ctx.guild.id)
        max_bets = (math.floor(points / 100.0) * 100) / 50
        current_bets = self.user_bets.query(
            {"guild_id": ctx.guild.id,
             "user": ctx.author.id,
             "result": None
             },
            projection={"_id": True}
        )

        current_bets = len(current_bets)

        if max_bets == 0:
            max_bets = 2

        if ctx.author.id == CREATOR or ctx.author.id in BETA_USERS:
            max_bets = max_bets + 2

        if current_bets and current_bets > max_bets:
            msg = (f"The maximum number of open bets allowed is determined by your BSEddie total. The more you have,"
                   f" the more open bets you're allowed to maintain. It looks like you already have the maximum "
                   f"number of open bets. You'll have to wait until they're closed or you have more BSEddies.")
            await ctx.send(content=msg, hidden=True)
            return

        if (option_one_name and not option_two_name) or (not option_one_name and option_two_name):
            msg = (f"If you're providing custom outcome names - you must provide at least two outcomes.\n"
                   f"Additionally, you must provide the outcomes sequentially "
                   f"(ie, outcome_one, then outcome_two, and then outcome_three, and then outcome_four.)")
            await ctx.send(content=msg, hidden=True)
            return

        if not option_one_name and not option_two_name:
            option_dict = copy.deepcopy(self.default_two_options)
        elif (option_one_name and option_two_name) and not option_three_name:
            option_dict = copy.deepcopy(self.default_two_options)
            keys = list(option_dict.keys())
            option_dict[keys[0]]["val"] = option_one_name
            option_dict[keys[1]]["val"] = option_two_name
        elif option_one_name and option_two_name and option_three_name:
            option_dict = {self.multiple_options_emojis[0]: {"val": option_one_name},
                           self.multiple_options_emojis[1]: {"val": option_two_name},
                           self.multiple_options_emojis[2]: {"val": option_three_name}}
            if option_four_name:
                option_dict[self.multiple_options_emojis[3]] = {"val": option_four_name}
        else:
            msg = (f"If you're providing custom outcome names - you must provide at least two outcomes.\n"
                   f"Additionally, you must provide the outcomes sequentially "
                   f"(ie, outcome_one, then outcome_two, and then outcome_three, and then outcome_four.)")
            await ctx.send(content=msg, hidden=True)
            return

        if timeout_str is None:
            timeout = datetime.datetime.now() + datetime.timedelta(minutes=5)
        else:
            timeout_str = timeout_str.strip()
            match = re.match(r"\d{1,5}(s|m|h|d)", timeout_str)
            if not match:
                msg = ("Your timeout string was incorrectly formatted. Needs to be 1 - 5 digits "
                       "and then either a s, m, h, or d "
                       "to signify seconds, minutes, hours, or days respectively.")
                await ctx.send(content=msg, hidden=True)
                return
            g = match.group()
            if "s" in g:
                dt_key = {"seconds": int(g.replace("s", ""))}
            elif "m" in g:
                dt_key = {"minutes": int(g.replace("m", ""))}
            elif "h" in g:
                dt_key = {"hours": int(g.replace("h", ""))}
            elif "d" in g:
                dt_key = {"days": int(g.replace("d", ""))}
            else:
                dt_key = {}
            timeout = datetime.datetime.now() + datetime.timedelta(**dt_key)

        private = ctx.channel_id in PRIVATE_CHANNELS_IDS

        bet = self.user_bets.create_new_bet(
            ctx.guild.id,
            ctx.author.id,
            bet_title,
            options=list(option_dict.keys()),
            option_dict=option_dict,
            timeout=timeout,
            private=private
        )

        embed = self.embed_manager.get_bet_embed(ctx.guild, bet["bet_id"], bet)

        member = ctx.guild.get_member(ctx.author.id)
        # embed.set_author(name=member.name)

        content = f"Bet created by {member.mention}"

        # await ctx.send(content=f"Bet created: {bet_title}", hidden=True)
        message = await ctx.channel.send(content=content, embed=embed)

        self.user_bets.update(
            {"_id": bet["_id"]},
            {"$set": {"message_id": message.id, "channel_id": message.channel.id}}
        )
        for emoji in option_dict:
            await message.add_reaction(emoji)


class BSEddiesPlaceEvent(BSEddies):
    def __init__(self, client, guilds, logger, beta_mode=False):
        super().__init__(client, guilds, logger, beta_mode=beta_mode)

    async def place_bet(
            self,
            ctx: discord_slash.context.SlashContext,
            bet_id: str,
            amount: int,
            emoji: str,
    ):
        """
        Main method for placing a bet.

        Validates that a bet exists, is active and that the user has the right amount of BSEddies.
        It also checks that the bet being placed is either new, or the same as the existing bet the user
        has for this bet.

        :param ctx:
        :param bet_id:
        :param amount:
        :param emoji:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        guild = ctx.guild  # type: discord.Guild
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

        if not bet:
            msg = f"This bet doesn't exist."
            await ctx.send(content=msg, hidden=True)
            return

        if not bet["active"]:
            msg = f"Your reaction on **Bet {bet_id}** failed as the bet is closed for new bets."
            await ctx.send(content=msg, hidden=True)
            return

        emoji = emoji.strip()

        if emoji not in bet["option_dict"]:
            msg = f"Your reaction on **Bet {bet_id}** failed as that reaction isn't a valid outcome."
            await ctx.send(content=msg, hidden=True)
            return

        success = self.user_bets.add_better_to_bet(bet_id, guild.id, ctx.author.id, emoji, amount)

        if not success["success"]:
            msg = f"Your reaction on **Bet {bet_id}** failed cos __{success['reason']}__?"
            await ctx.send(content=msg, hidden=True)
            return False

        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
        channel = guild.get_channel(bet["channel_id"])
        message = channel.get_partial_message(bet["message_id"])
        embed = self.embed_manager.get_bet_embed(guild, bet_id, bet)
        await message.edit(embed=embed)
