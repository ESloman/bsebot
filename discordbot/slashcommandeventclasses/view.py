
import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from mongo.datatypes import User


class View(BSEddies):
    """
    Class for handling `/view` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.dmable = True
        self.activity_type = ActivityTypes.BSEDDIES_VIEW
        self.help_string = "View your eddies for the server"
        self.command_name = "view"

    def _construct_guild_message(self, user: User) -> str:
        """
        Constructs the `View` message for a given user and guild

        Args:
            user (User): the DB Uer object

        Returns:
            str: the constructed message
        """
        guild_db = self.guilds.get_guild(user["guild_id"])
        if not guild_db:
            return "Guild didn't exist in guilds collection - probbaly just a debug error"
        pending = self.user_bets.get_user_pending_points(user["uid"], user["guild_id"])
        msg = (
            f"**{guild_db['name']}**\n"
            f"You have **{user['points']}** :money_with_wings:`BSEDDIES`:money_with_wings:!"
            f"\nAdditionally, you have `{pending}` points on 'pending bets'.\n\n"
            f"The _absolute highest_ amount of eddies you've ever had was `{user.get('high_score', 0)}`!."
        )
        return msg

    async def view(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling view slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        _user = None
        if not ctx.guild:
            # no guild - workout if user is in more than one guild or not
            users = self.user_points.find_user_guildless(ctx.author.id)
            if len(users) > 1:
                return await self.view_guildless(ctx, users)
            elif len(users) == 1:
                _user = users[0]
            else:
                # no guilds at all?
                await ctx.respond("We do not share any guilds together.")
                return

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.BSEDDIES_VIEW)

        if not _user:
            _user = self.user_points.find_user(ctx.author.id, ctx.guild.id)

        msg = self._construct_guild_message(_user)
        await ctx.respond(content=msg, ephemeral=True)

    async def view_guildless(self, ctx: discord.ApplicationContext, users: list[User]) -> None:
        """
        Sends multiple messages for each guild the user is in

        Args:
            ctx (discord.ApplicationContext): the context to respond to
            users (list[User]): the list of users
        """
        await ctx.respond("Eddies for all your guilds:")

        for _user in users:
            msg = self._construct_guild_message(_user)
            await ctx.followup.send(content=msg)
