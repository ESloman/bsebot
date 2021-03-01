import datetime

import discord
from discord.ext import tasks, commands

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

    @tasks.loop(minutes=2)
    async def inactive_user_task(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        now = datetime.datetime.now()
        two_weeks_ago = now - datetime.timedelta(days=14)
        for guild_id in self.guilds:
            guild_obj = self.bot.get_guild(guild_id)  # type: discord.Guild

            all_users = self.user_points.query({"guild_id": guild_id})
            for user in all_users:

                user_obj = self.bot.get_user(user['uid'])  # type: discord.User
                interactions = [a for a in user["transaction_history"] if a["type"] in [2, 4, 9, 10]]
                if not interactions:
                    last_interaction = now - datetime.timedelta(days=30)
                else:
                    last_interaction = interactions[-1]["timestamp"]

                last_cull = user.get("last_cull_time")

                if last_interaction > two_weeks_ago:
                    # interacted recently
                    self.logger.info(f"{user['uid']} - {user_obj.display_name} last interacted within two weeks")
                    continue

                elif last_cull is not None and last_interaction < two_weeks_ago < last_cull:
                    # haven't interacted in two weeks but we culled within the last two weeks
                    self.logger.info(f"{user['uid']} - {user_obj.display_name} last interacted over two weeks"
                                     f" but was culled recently.")
                    continue

                elif last_interaction < two_weeks_ago and last_cull is None:
                    # in this siutation - the user has never been culled and last interacted more than two weeks ago
                    self.logger.info(f"{user['uid']} - {user_obj.display_name} hasn't interacted recently and has "
                                     f"never been culled.")
                    self.user_points.update({"_id": user["_id"]}, {"$set": {"last_cull_time": now}})

                elif last_interaction < two_weeks_ago and last_cull < two_weeks_ago:
                    # in this situation - the user was culled two weeks ago and last interacted two weeks ago
                    self.logger.info(f"{user['uid']} - {user_obj.display_name} hasn't interacted recently and hasn't "
                                     f"been culled in two weeks either.")
                    self.user_points.update({"_id": user["_id"]}, {"$set": {"last_cull_time": now}})

    @inactive_user_task.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
