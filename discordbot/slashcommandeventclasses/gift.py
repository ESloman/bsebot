"""Gift slash command."""

import logging

import discord

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies


class Gift(BSEddies):
    """Class for handling `/bseddies gift` command."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.activity_type = ActivityTypes.BSEDDIES_GIFT
        self.help_string = "Gift some eddies to a friend"
        self.command_name = "gift"

    async def gift_eddies(
        self,
        ctx: discord.ApplicationContext | discord.Interaction,
        friend: discord.User,
        amount: int,
    ) -> None:
        """Function for handling a 'gift eddies' event.

        We make sure that the user initiating the command has enough BSEddies to give to a friend
        and then we simply increment their friend's BSEddies and decrement theirs.

        :param ctx: slash command context
        :param friend: discord.User for the friend to give eddies to
        :param amount: the amount of eddies to give
        :return: None
        """
        if not await self._handle_validation(ctx, friend=friend, amount=amount):
            return

        self._add_event_type_to_activity_history(
            ctx.user,
            ctx.guild_id,
            ActivityTypes.BSEDDIES_GIFT,
            friend_id=friend.id,
            amount=amount,
        )

        if type(ctx) is discord.ApplicationContext:
            response = ctx.respond
        elif type(ctx) is discord.Interaction:
            response = ctx.response.send_message
        else:
            response = ctx.respond

        points = self.user_points.get_user_points(ctx.user.id, ctx.guild.id)
        if points < amount:
            msg = "You have insufficient points to perform that action."
            await response(content=msg, ephemeral=True, delete_after=10)
            return

        if not friend.dm_channel:
            await friend.create_dm()
        try:
            msg = f"**{ctx.user.name}** just gifted you `{amount}` eddies!!"
            await friend.send(content=msg, silent=True)
        except discord.Forbidden:
            pass

        self.user_points.increment_points(
            ctx.user.id,
            ctx.guild.id,
            amount * -1,
            TransactionTypes.GIFT_GIVE,
            friend_id=friend.id,
        )
        self.user_points.increment_points(
            friend.id,
            ctx.guild.id,
            amount,
            TransactionTypes.GIFT_RECEIVE,
            friend_id=ctx.user.id,
        )

        await response(content=f"Eddies transferred to `{friend.name}`!", ephemeral=True, delete_after=5)
