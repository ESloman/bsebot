"""Activity Changer task."""

import asyncio
import datetime
import random
from logging import Logger
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class ActivityChanger(BaseTask):
    """Class for activity changer."""

    def __init__(
        self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask], start: bool = True
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task automatically or not. Defaults to True.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)

        self.task = self.activity_changer

        self.default_activity = discord.Activity(
            name="conversations",
            state="Listening",
            type=discord.ActivityType.listening,
            details="Waiting for commands!",
        )

        if start:
            self.task.start()

    @tasks.loop(hours=1)
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
            all_activities = self.bot_activities.get_all_activities()

            # crude way of weighting
            total = len(all_activities)
            weights = []

            for activity in all_activities:
                weight = total - activity.count
                # just make sure that the weight is non-zero
                if weight < 0:
                    weight = 0
                if weight == 0:
                    weight += 0.1
                weights.append(weight)

            _activity = random.choices(all_activities, weights)[0]

            new_activity = {"name": _activity.name, "details": "Waiting for commands!"}

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
