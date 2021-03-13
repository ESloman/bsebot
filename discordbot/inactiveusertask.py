import datetime
import math

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BSE_SERVER_ID, CREATOR
from mongo.bsepoints import UserPoints, UserBets


class BSEddiesInactiveUsers(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.user_points = UserPoints()
        self.user_bets = UserBets()
        self.logger = logger
        self.guilds = guilds
        self.safe_interactions = [2, 3, 4, 5, 8, 9, 10, 11, 12, 16, 17, 18, 19]
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
        points_to_take = math.floor(current_points * 0.75)
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

        if points_to_cull == 0:
            return total_culled_points

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

    @tasks.loop(hours=2)
    async def inactive_user_task(self):
        """
        Task that makes sure inactive users don't get too high in the leaderboards. We half their points every week
        to keep them down.
        :return:
        """

        self.logger.info("Beginning check for inactive users.")

        now = datetime.datetime.now()
        one_week_ago = now - datetime.timedelta(days=5)

        for guild_id in self.guilds:

            users_who_will_be_culled = []
            users_who_will_gain_points = []
            total_culled_points = 0

            all_users = self.user_points.query({"guild_id": guild_id})
            for user in all_users:

                user_obj = self.bot.get_user(user['uid'])  # type: discord.User

                if user_obj is None:
                    continue

                pending_points = self.user_bets.get_user_pending_points(user["uid"], guild_id)

                if pending_points > 0:
                    time_limit = now - datetime.timedelta(days=10)
                else:
                    time_limit = one_week_ago

                interactions = [
                    a for a in user["transaction_history"] if a["type"] not in [6, 11, 13, 14, 15, 99]
                ]
                if not interactions:
                    last_interaction = now - datetime.timedelta(days=30)
                else:
                    last_interaction = interactions[-1]["timestamp"]

                last_cull = user.get("last_cull_time")

                if last_interaction > time_limit:
                    # interacted recently
                    users_who_will_gain_points.append((user["_id"], user_obj))

                    # this is where we can do 24 hour warnings
                    twenty_four_hour_warning = time_limit + datetime.timedelta(days=1)
                    if last_interaction < twenty_four_hour_warning:

                        if last_cull and time_limit < last_cull:
                            continue 

                        if not user.get("cull_warning"):
                            # OH UH
                            message = (
                                f"It looks like you haven't used any eddies in a while. If you don't use them in"
                                f" the next **24** hours, your eddies will be culled and `75%` of your eddies "
                                f"will be distributed amongst the other server members that are using eddies."
                                f"\n\n"
                                f"Valid interaction types: "
                                f"{', '.join([f'`{TransactionTypes(n).name}`' for n in self.safe_interactions])}"
                            )
                            self.logger.info(f"Sending cull warning to {user['uid']}")
                            self.user_points.update({"_id": user["_id"]}, {"$set": {"cull_warning": True}})
                            if user.get("daily_eddies"):
                                try:
                                    await user_obj.send(content=message)
                                except discord.Forbidden:
                                    pass
                    else:
                        if user.get("cull_warning"):
                            self.user_points.update({"_id": user["_id"]}, {"$set": {"cull_warning": False}})

                    continue

                elif user["points"] <= 10:
                    # we don't care if the user has this many points
                    continue

                elif last_cull is not None and last_interaction < time_limit < last_cull:
                    # haven't interacted in the last week but we already culled them more recently than that
                    continue

                elif last_interaction < time_limit and last_cull is None:
                    # user hasn't interacted in the last week and we've never culled them
                    total_culled_points = self.__cull_user(
                        user, total_culled_points, users_who_will_be_culled, now, user_obj
                    )

                elif last_interaction < time_limit and last_cull is not None and last_cull < time_limit:
                    # user hasn't interacted in the last week and we culled them over a week ago
                    total_culled_points = self.__cull_user(
                        user, total_culled_points, users_who_will_be_culled, now, user_obj
                    )
                else:
                    continue

            if total_culled_points == 0:
                continue

            if len(users_who_will_gain_points) == 0:
                continue

            points_each = math.floor(total_culled_points / len(users_who_will_gain_points))

            if points_each == 0:
                points_each = 1

            self.logger.debug(f"Each user ({len(users_who_will_gain_points)}) will gain {points_each}")

            prt = "has" if len(users_who_will_be_culled) == 1 else "have all"

            message = (f"{', '.join([f'**{u[1].display_name}**' for u in users_who_will_be_culled])} {prt} lost a "
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
