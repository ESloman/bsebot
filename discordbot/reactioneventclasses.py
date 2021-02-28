import datetime
import re

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.baseeventclass import BaseEvent


class BaseReactionEvent(BaseEvent):
    """
    Base class for handling on_reaction_add events from Discord
    """

    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)


class LeaderBoardReactionEvent(BaseEvent):
    """
    Class for handling user reactions to leaderboards
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def handle_leaderboard_reaction(self, message: discord.Message, guild: discord.Guild) -> None:
        """
        Here we do a basic check to make sure that a user is reacting to the message - if so, we update the leaderboard.

        :param message:
        :param guild:
        :return:
        """
        if not message.author.bot:
            return

        content = self.embed_manager.get_leaderboard_embed(guild, None)
        await message.edit(content=content)
        return


class BetReactionEvent(BaseEvent):
    """
    Class for handling user reactions to bets
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def handle_bet_reaction_event(
            self,
            message: discord.Message,
            guild: discord.Guild,
            channel: discord.TextChannel,
            reaction_emoji: str,
            user: discord.User,
    ) -> None:
        """
        Here we do some basic checks about the bet being reacted to. We check if it's active, if the emoji is relevant,
        and then we attempt to add the user to the bet.

        We inform the user if it was successful or not via Direct Message.

        We remove all reactions to the message if we can.

        :param message:
        :param guild:
        :param channel:
        :param reaction_emoji:
        :param user:
        :return:
        """
        embed = message.embeds[0]  # type: discord.Embed
        bet_id = re.findall(r"(?<=Bet ID: )\d\d\d\d", embed.description)[0]
        bet = self.user_bets.get_bet_from_id(guild.id, bet_id)

        link = f"https://discordapp.com/channels/{guild.id}/{channel.id}/{message.id}"

        # make sure the bet is active
        if not bet["active"]:
            msg = f"Your reaction on **Bet {bet_id}** _(<{link}>)_ failed as the bet is closed for new bets."
            if not user.dm_channel:
                await user.create_dm()
            try:
                await user.send(content=msg)
            except discord.errors.Forbidden:
                pass
            await message.remove_reaction(reaction_emoji, user)
            return

        # make sure that the reaction is a valid outcome
        if reaction_emoji not in bet['option_dict']:
            msg = f"Your reaction on **Bet {bet_id}** _(<{link}>)_ failed as that reaction isn't a valid outcome."
            if not user.dm_channel:
                await user.create_dm()
            try:
                await user.send(content=msg)
            except discord.errors.Forbidden:
                pass
            await message.remove_reaction(reaction_emoji, user)
            return

        # do the bet
        ret = self.user_bets.add_better_to_bet(bet_id, guild.id, user.id, reaction_emoji, 1)

        if ret["success"]:
            new_bet = self.user_bets.get_bet_from_id(guild.id, bet_id)
            embed = self.embed_manager.get_bet_embed(guild, bet_id, new_bet)

            await message.edit(embed=embed)

            # add to transaction history
            self.user_points.append_to_transaction_history(
                user.id,
                guild.id,
                {
                    "type": TransactionTypes.BET_PLACE,
                    "amount": -1,
                    "timestamp": datetime.datetime.now(),
                    "bet_id": bet_id,
                    "comment": "Bet placed through reaction",
                }
            )

        await message.remove_reaction(reaction_emoji, user)
