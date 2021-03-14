import datetime
import re

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.baseeventclass import BaseEvent
from discordbot.constants import BSEDDIES_KING_ROLES


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


class HighScoreReactionEvent(BaseEvent):
    """
    Class for handling user reactions to high score boards
    """
    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    async def handle_highscore_reaction(self, message: discord.Message, guild: discord.Guild) -> None:
        """
        Here we do a basic check to make sure that a user is reacting to the message - if so, we update the high score.

        :param message:
        :param guild:
        :return:
        """
        if not message.author.bot:
            return

        content = self.embed_manager.get_highscore_embed(guild, None)
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


class RevolutionReactionEvent(BaseEvent):
    """
    Class for handling user reactions to revolution events
    """

    def __init__(self, client, guild_ids, logger, beta_mode=False):
        super().__init__(client, guild_ids, logger, beta_mode=beta_mode)

    @staticmethod
    async def _send_message(user: discord.User, message):
        """
        Static method for sending a user a DM. We need to do this a lot in this class so it makes
        sense to have a dedicated method.
        :param user:
        :param message:
        :return:
        """
        if not user.dm_channel:
            await user.create_dm()
        try:
            await user.send(content=message)
        except discord.errors.Forbidden:
            pass

    async def handle_revolution_reaction(self, message: discord.Message, guild: discord.Guild, user: discord.User):
        """
        Function for handling revolution reaction. Basically, a user is buying a 'ticket' here.

        We do some basic checking. The user must:
            - be buying a ticket for a non-expired event
            - not be the king
            - have enough eddies
            - not have already bought a ticket

        If the user passes all that - we buy them a ticket.

        :param message:
        :param guild:
        :param user:
        :return:
        """
        event_id = re.findall(r"(?<=\*\*Event ID\*\*: `)\d\d\d", message.content)[0]
        event = self.revolutions.get_event(guild.id, event_id)

        if not event["open"]:
            await self._send_message(user, "Unfortunately, this event has expired and you can no longer buy tickets.")
            await message.remove_reaction("🎟️", user)
            return

        now = datetime.datetime.now()

        if event["expired"] < now:
            await self._send_message(user, "Unfortunately, this event has expired and you can no longer buy tickets.")
            await message.remove_reaction("🎟️", user)
            return

        our_user = self.user_points.find_user(user.id, guild.id, {"points": True, "king": True})

        if our_user.get("king", False):
            await self._send_message(user, "Unfortunately, you are the KING and cannot buy tickets for this event.")
            await message.remove_reaction("🎟️", user)
            return

        if our_user["points"] < event["ticket_cost"]:
            await self._send_message(user, "Unfortunately, you don't have enough eddies to buy a ticket.")
            await message.remove_reaction("🎟️", user)
            return

        if user.id in event["ticket_buyers"]:
            await self._send_message(user, "Unfortunately, you have already bought a ticket for this event.")
            await message.remove_reaction("🎟️", user)
            return

        if event["chance"] < 75:
            self.revolutions.increment_chance(event_id, guild.id, 5)
        self.revolutions.increment_eddies_total(event_id, guild.id, event["ticket_cost"])
        self.revolutions.add_user_to_buyers(event_id, guild.id, user.id)
        self.user_points.decrement_points(user.id, guild.id, event["ticket_cost"])

        self.user_points.append_to_transaction_history(
            user.id, guild.id,
            {
                "type": TransactionTypes.REV_TICKET_BUY,
                "amount": event["ticket_cost"] * -1,
                "event_id": event["event_id"],
                "timestamp": datetime.datetime.now(),
            }
        )

        new_event = self.revolutions.get_event(guild.id, event_id)
        king = self.user_points.get_current_king(guild.id)

        king_user = await self.client.fetch_user(king["uid"])  # type: discord.User
        role = guild.get_role(BSEDDIES_KING_ROLES[guild.id])

        edited_message = self.embed_manager.get_revolution_message(king_user, role, new_event)
        await message.edit(content=edited_message)
        await self._send_message(user, "Congrats - you bought a ticket! 🎟")
