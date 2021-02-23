import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSEDDIES_KING_ROLES
from mongo.bsepoints import UserPoints


class BSEddiesKing(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.user_points = UserPoints()
        self.logger = logger
        self.guilds = guilds
        self.king_checker.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.king_checker.cancel()

    @tasks.loop(minutes=10)
    async def king_checker(self):
        """
        Loop that takes all our active bets and ensures they haven't expired.
        If they have expired - they get closed.
        :return:
        """
        for guild_id in self.guilds:
            guild_obj = self.bot.get_guild(guild_id)  # type: discord.Guild
            role_id = BSEDDIES_KING_ROLES[guild_id]

            role = guild_obj.get_role(role_id)  # type: discord.Role
            current_king = None
            if len(role.members) > 1:
                self.logger.info("We have multiple people with this role - purging the list.")
                for member in role.members:  # type: discord.Member
                    await member.remove_roles(role, reason="User assigned themself this role and they are NOT king.")
            elif len(role.members) == 1:
                current_king = role.members[0].id

            users = self.user_points.get_all_users_for_guild(guild_id)
            top_user = sorted(users, key=lambda x: x["points"], reverse=True)[0]
            if current_king is not None and top_user["uid"] != current_king:
                current = guild_obj.get_member(current_king)  # type: discord.Member
                self.logger.info(f"Removing a king: {current.display_name}")
                await current.remove_roles(role, reason="User is not longer King!")
                current_king = None

            if current_king is None:
                new = guild_obj.get_member(top_user["uid"])  # type: discord.Member
                self.logger.info(f"Adding a new king: {new.display_name}")
                await new.add_roles(role, reason="User is now KING!")

    @king_checker.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
