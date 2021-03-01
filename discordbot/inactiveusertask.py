import datetime
import math

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID, CREATOR
from mongo.bsepoints import UserPoints


class BSEddiesInactiveUsers(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.user_points = UserPoints()
        self.logger = logger
        self.guilds = guilds
        self.inactive_user_task.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.inactive_user_task.cancel()

    @staticmethod
    def __calc_eddie_to_take(user):
        current_points = user["points"]
        points_to_take = math.floor(current_points / 2)
        remaining = current_points - points_to_take

        if remaining < 10:
            addition = 10 - remaining
            points_to_take -= addition
        return points_to_take

    @tasks.loop(hours=1)
    async def inactive_user_task(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        now = datetime.datetime.now()
        two_weeks_ago = now - datetime.timedelta(days=14)
        for guild_id in self.guilds:
            guild_obj = self.bot.get_guild(guild_id)  # type: discord.Guild

            users_who_will_be_culled = []
            users_who_will_gain_points = []
            total_culled_points = 0

            all_users = self.user_points.query({"guild_id": guild_id})
            for user in all_users:

                if user["points"] <= 10:
                    # we don't care if the user has this many points
                    continue

                user_obj = self.bot.get_user(user['uid'])  # type: discord.User

                interactions = [a for a in user["transaction_history"] if a["type"] in [2, 4, 9, 10]]
                if not interactions:
                    last_interaction = now - datetime.timedelta(days=30)
                else:
                    last_interaction = interactions[-1]["timestamp"]

                last_cull = user.get("last_cull_time")

                if last_interaction > two_weeks_ago:
                    # interacted recently
                    users_who_will_gain_points.append((user["_id"], user_obj))
                    continue

                elif last_cull is not None and last_interaction < two_weeks_ago < last_cull:
                    # haven't interacted in two weeks but we culled within the last two weeks
                    continue

                elif last_interaction < two_weeks_ago and last_cull is None:
                    # in this siutation - the user has never been culled and last interacted more than two weeks ago
                    points_to_cull = self.__calc_eddie_to_take(user)
                    users_who_will_be_culled.append((user["_id"], user_obj))
                    total_culled_points += points_to_cull
                    self.logger.info(f"{user_obj.display_name} will be deducted {total_culled_points} for inactivity.")
                    self.user_points.update({"_id": user["_id"]}, {"$set": {"last_cull_time": now}})

                elif last_interaction < two_weeks_ago and last_cull is not None and last_cull < two_weeks_ago:
                    # in this situation - the user was culled two weeks ago and last interacted two weeks ago
                    points_to_cull = self.__calc_eddie_to_take(user)
                    users_who_will_be_culled.append((user["_id"], user_obj))
                    total_culled_points += points_to_cull
                    self.logger.info(f"{user_obj.display_name} will be deducted {total_culled_points} for inactivity.")
                    self.user_points.update({"_id": user["_id"]}, {"$set": {"last_cull_time": now}})
                else:
                    continue

            if total_culled_points == 0:
                return

            if len(users_who_will_gain_points) == 0:
                return

            points_each = math.floor(total_culled_points / len(users_who_will_gain_points))
            self.logger.debug(f"Each user ({len(users_who_will_gain_points)}) will gain {points_each}")

            message = (f"{', '.join([f'**{u[1].display_name}**' for u in users_who_will_be_culled])} have all lost a "
                       f"share of their eddies due to inactivity. This share has been redistributed amongst the active "
                       f"users. Because of this - you have gained `{points_each}`! Happy betting.")

            for lucky_user in users_who_will_gain_points:
                user_obj = lucky_user[1]  # type: discord.User
                # self.user_points.increment_points(user_obj.id, BSE_SERVER_ID, points_each)
                if user_obj.id == CREATOR:
                    await user_obj.send(content=message)

    @inactive_user_task.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
