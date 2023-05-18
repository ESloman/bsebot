
import asyncio
import datetime
import random
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class ActivityChanger(BaseTask):

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)

        self.task = self.activity_changer

        self.default_activity = discord.Activity(**{
            "name": "conversations",
            "state": "Listening",
            "type": discord.ActivityType.listening,
            "details": "Waiting for commands!"
        })

        self.task.start()

    @tasks.loop(hours=1)
    async def activity_changer(self):
        """
        Loop that occasionally changes the activity.
        """

        now = datetime.datetime.now()
        if 0 < now.hour < 6:
            # make it really rare for activity to change 'overnight'
            threshold = 0.9
        else:
            threshold = 0.45

        _rand = random.random()

        if _rand <= threshold:
            # keep default
            activity = self.default_activity
        else:
            # pick one randomly from database
            all_activities = self.bot_activities.get_all_activities()

            # crude way of weighting
            total = len(all_activities)
            weights = []

            for activity in all_activities:
                weight = total - activity["count"]
                # just make sure that the weight is non-zero
                weight += 0.1
                weights.append(weight)

            _activity = random.choices(all_activities, weights)[0]

            new_activity = {"name": _activity["name"], "details": "Waiting for commands!"}

            match _activity["category"]:
                case "listening":
                    new_activity["state"] = "Listening"
                    new_activity["type"] = discord.ActivityType.listening
                case "watching":
                    new_activity["state"] = "Watching"
                    new_activity["type"] = discord.ActivityType.watching
                case "playing":
                    new_activity["state"] = "Playing"
                    new_activity["type"] = discord.ActivityType.playing
                case _:
                    return

            activity = discord.Activity(**new_activity)
            # increment count for this selected activity
            self.bot_activities.update({"_id": _activity["_id"]}, {"$inc": {"count": 1}})

        await self.bot.change_presence(activity=activity)

    @activity_changer.before_loop
    async def before_activity_changer(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
