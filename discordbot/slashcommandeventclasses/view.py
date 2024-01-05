"""View slash command."""

import logging

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from mongo.datatypes import UserDB


class View(BSEddies):
    """Class for handling `/view` commands."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)
        self.dmable = True
        self.activity_type = ActivityTypes.BSEDDIES_VIEW
        self.help_string = "View your eddies for the server"
        self.command_name = "view"

    def _construct_guild_message(self, user: UserDB) -> str:
        """Constructs the `View` message for a given user and guild.

        Args:
            user (User): the DB Uer object

        Returns:
            str: the constructed message
        """
        guild_db = self.guilds.get_guild(user.guild_id)
        if not guild_db:
            return "Guild didn't exist in guilds collection - probbaly just a debug error"
        pending = self.user_bets.get_user_pending_points(user.uid, user.guild_id)
        return (
            f"**{guild_db.name}**\n"
            f"You have **{user.points}** :money_with_wings:`BSEDDIES`:money_with_wings:!"
            f"\nAdditionally, you have `{pending}` points on 'pending bets'.\n\n"
            f"The _absolute highest_ amount of eddies you've ever had was `{user.high_score}`!."
        )

    async def view(self, ctx: discord.ApplicationContext) -> None:
        """Basic view method for handling view slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return None

        _user = None
        if not ctx.guild:
            # no guild - workout if user is in more than one guild or not
            users = self.user_points.find_user_guildless(ctx.author.id)
            if len(users) > 1:
                return await self.view_guildless(ctx, users)

            if len(users) == 1:
                _user = users[0]
            else:
                # no guilds at all?
                await ctx.respond("We do not share any guilds together.")
                return None

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_VIEW)

        if not _user:
            _user = self.user_points.find_user(ctx.author.id, ctx.guild.id)

        msg = self._construct_guild_message(_user)
        await ctx.respond(content=msg, ephemeral=True)
        return None

    async def view_guildless(self, ctx: discord.ApplicationContext, users: list[UserDB]) -> None:
        """Sends multiple messages for each guild the user is in.

        Args:
            ctx (discord.ApplicationContext): the context to respond to
            users (list[User]): the list of users
        """
        await ctx.respond("Eddies for all your guilds:")

        for _user in users:
            msg = self._construct_guild_message(_user)
            await ctx.followup.send(content=msg)
