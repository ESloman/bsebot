import datetime

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSEDDIES_KING_ROLES
from mongo.bsepoints import UserPoints


class BSEddiesKingTask(commands.Cog):
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

    @tasks.loop(minutes=1)
    async def king_checker(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        for guild_id in self.guilds:
            guild_obj = await self.bot.fetch_guild(guild_id)  # type: discord.Guild
            guild = self.bot.get_guild(guild_id)
            member_ids = [member.id for member in guild.members]

            role_id = BSEDDIES_KING_ROLES[guild_id]

            role = guild.get_role(role_id)  # type: discord.Role
            current_king = None
            prev_king_id = None
            if len(role.members) > 1:
                self.logger.info("We have multiple people with this role - purging the list.")
                for member in role.members:  # type: discord.Member
                    await member.remove_roles(role, reason="User assigned themself this role and they are NOT king.")
            elif len(role.members) == 1:
                current_king = role.members[0].id

            users = self.user_points.get_all_users_for_guild(guild_id)
            users = [u for u in users if not u.get("inactive") and u["uid"] in member_ids]
            top_user = sorted(users, key=lambda x: x["points"], reverse=True)[0]

            if current_king is not None and top_user["uid"] == current_king:
                # current king is fine
                return

            new = await guild_obj.fetch_member(top_user["uid"])  # type: discord.Member

            if current_king is not None and top_user["uid"] != current_king:
                prev_king_id = current_king
                current = await guild_obj.fetch_member(current_king)  # type: discord.Member
                self.logger.info(f"Removing a king: {current.display_name}")

                await current.remove_roles(role, reason="User is not longer King!")

                self.user_points.set_king_flag(current_king, guild_id, False)

                message = (f"You have been **DETHRONED** - {new.display_name} is now the "
                           f"KING of {guild_obj.name}! :crown:")
                await current.send(content=message)

                activity = {
                    "type": ActivityTypes.KING_LOSS,
                    "timestamp": datetime.datetime.now(),
                    "comment": f"Losing King to {top_user['uid']}"
                }

                self.user_points.append_to_activity_history(current_king, guild_id, activity)
                current_king = None

            if current_king is None:
                self.logger.info(f"Adding a new king: {new.display_name}")

                activity = {
                    "type": ActivityTypes.KING_GAIN,
                    "timestamp": datetime.datetime.now(),
                    "comment": f"Taking King from {prev_king_id}"
                }

                self.user_points.append_to_activity_history(top_user['uid'], guild_id, activity)
                await new.add_roles(role, reason="User is now KING!")

                self.user_points.set_king_flag(top_user['uid'], guild_id, True)

                message = f"You are now the KING of {guild_obj.name}! :crown:"
                await new.send(content=message)

    @king_checker.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
