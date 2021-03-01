import datetime
import math

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import TransactionTypes
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
    def __calc_eddie_to_take(user: dict):
        """
        Makes sure we take at least half the user's points - but don't go below 10
        :param user: user dictionary
        :return: int
        """
        current_points = user["points"]
        points_to_take = math.floor(current_points / 2)
        remaining = current_points - points_to_take

        if remaining < 10:
            addition = 10 - remaining
            points_to_take -= addition
        return points_to_take

    def __cull_user(self, user, total_culled_points, users_who_will_be_culled, now, user_obj):
        """
        Method for culling a user's points.
        :param user:
        :param total_culled_points:
        :param users_who_will_be_culled:
        :param now:
        :param user_obj:
        :return:
        """
        points_to_cull = self.__calc_eddie_to_take(user)
        users_who_will_be_culled.append((user["_id"], user_obj))
        total_culled_points += points_to_cull
        self.logger.info(f"{user_obj.display_name} will be deducted {points_to_cull} for inactivity.")
        self.user_points.update({"_id": user["_id"]}, {"$set": {"last_cull_time": now}})

        self.user_points.decrement_points(user_obj.id, BSE_SERVER_ID, points_to_cull)

        self.user_points.append_to_transaction_history(
            user_obj.id, BSE_SERVER_ID,
            {
                "type": TransactionTypes.POINT_ROT_LOSS,
                "amount": points_to_cull * -1,
                "timestamp": now,
                "comment": "Gained eddies due to other user's inactivity"
            }
        )

        return total_culled_points

    @tasks.loop(hours=8)
    async def inactive_user_task(self):
        """
        Task that makes sure inactive users don't get too high in the leaderboards. We half their points every week
        to keep them down.
        :return:
        """

        self.logger.info("Beginning check for inactive users.")

        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=7)

        for guild_id in self.guilds:

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

                if last_interaction > one_week_ago:
                    # interacted recently
                    users_who_will_gain_points.append((user["_id"], user_obj))
                    continue

                elif last_cull is not None and last_interaction < one_week_ago < last_cull:
                    # haven't interacted in the last week but we already culled them more recently than that
                    continue

                elif last_interaction < one_week_ago and last_cull is None:
                    # user hasn't interacted in the last week and we've never culled them
                    total_culled_points = self.__cull_user(
                        user, total_culled_points, users_who_will_be_culled, now, user_obj
                    )

                elif last_interaction < one_week_ago and last_cull is not None and last_cull < one_week_ago:
                    # user hasn't interacted in the last week and we culled them over a week ago
                    total_culled_points = self.__cull_user(
                        user, total_culled_points, users_who_will_be_culled, now, user_obj
                    )
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
                self.user_points.increment_points(user_obj.id, BSE_SERVER_ID, points_each)

                self.user_points.append_to_transaction_history(
                    user_obj.id, BSE_SERVER_ID,
                    {
                        "type": TransactionTypes.POINT_ROT_GAIN,
                        "amount": points_each,
                        "timestamp": now,
                        "comment": "Gained eddies due to other user's inactivity"
                    }
                )
                try:
                    await user_obj.send(content=message)
                except discord.Forbidden:
                    pass
        self.logger.info("Finished checking for inactive users")

    @inactive_user_task.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
