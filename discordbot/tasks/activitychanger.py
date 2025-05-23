"""Activity Changer task."""

import asyncio
import datetime
import random
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask, TaskSchedule


class ActivityChanger(BaseTask):
    """Class for activity changer."""

    def __init__(self, bot: BSEBot, startup_tasks: list[BaseTask], start: bool = False) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task automatically or not. Defaults to False.
        """
        super().__init__(bot, startup_tasks)

        self.schedule = TaskSchedule(range(7), range(24), 45)

        self.task = self.activity_changer

        self.default_activity = discord.Activity(
            name="conversations",
            state="Listening",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )

        if start:
            self.task.start()

    @tasks.loop(count=1)
    async def activity_changer(self) -> discord.Activity:
        """Loop that occasionally changes the activity."""
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        threshold = 0.9 if now.hour == 23 or 0 < now.hour < 8 else 0.65  # noqa: PLR2004

        _rand = random.random()

        if _rand <= threshold:
            # keep default
            activity = self.default_activity
        else:
            # pick one randomly from database
            self.logger.info("Selecting non-default activity")
            all_activities = self.bot_activities.get_all_activities()

            # crude way of weighting
            total = len(all_activities)
            self.logger.debug("Found %s activities as potential possibilities", total)

            total_usage = sum(activity.count for activity in all_activities)
            weights = []
            for activity in all_activities:
                weight = 1 - (activity.count / total_usage)
                # just make sure that the weight is non-zero
                weight = max(weight, 0)
                if weight == 0:
                    weight += 0.1
                weights.append(weight)

            if not weights:
                self.logger.warning("Weights was empty - no activities found?")
                return None

            self.logger.debug("Activity weigts: %s", weights)
            _activity = random.choices(all_activities, weights)[0]

            new_activity = {"name": _activity.name, "details": "Waiting for commands!"}
            self.logger.info("New activity name: %s, category: %s", _activity.name, _activity.category)

            match _activity.category:
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
                    return None

            activity = discord.Activity(**new_activity)
            # increment count for this selected activity
            self.bot_activities.update({"_id": _activity._id}, {"$inc": {"count": 1}})  # noqa: SLF001

        await self.bot.change_presence(activity=activity)
        return activity

    @activity_changer.before_loop
    async def before_activity_changer(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
