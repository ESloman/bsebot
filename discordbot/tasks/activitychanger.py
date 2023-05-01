
import asyncio
import random
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class ActivityChanger(BaseTask):

    activities_options = [
        (
            {
                "name": "conversations",
                "state": "Listening",
                "type": discord.ActivityType.listening,
                "details": "Waiting for commands!"
            },
            0.5
        ),
        (
            {
                "state": "Listening",
                "type": discord.ActivityType.listening,
                "details": "Waiting for commands!"
            },
            0.1
        ),
        (
            {
                "state": "Watching",
                "type": discord.ActivityType.watching,
                "details": "Waiting for commands!"
            },
            0.1
        ),
        (
            {
                "state": "Playing",
                "type": discord.ActivityType.playing,
                "details": "Waiting for commands!"
            },
            0.2
        ),
    ]

    watching_options = [
        "the latest Jenny Nicholson video",
        "hot tub streams",
        "the shitty Last of Us show",
        "you.",
    ]

    listening_options = [
        "Taylor Swift",
        "whale noises",
        "you.",
        "AI podcasts",
        "terrible financial advice",
    ]

    playing_options = [
        "Valorant",
        "Rocket League",
        "Stellaris",
        "with knives",
        "with myself.",
    ]

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)

        self.task = self.activity_changer
        self.task.start()

    @tasks.loop(minutes=60)
    async def activity_changer(self):
        """
        Loop that occasionally changes the activity.
        """

        # pick a new activity from the list of activities
        # these are weighted
        # default is more likely
        new_activity = random.choices(
            [act[0] for act in self.activities_options], [act[1] for act in self.activities_options]
        )[0]

        if "name" not in new_activity:
            # need to pick activity name randomly
            match new_activity["state"]:
                case "Listening":
                    name = random.choice(self.listening_options)
                case "Watching":
                    name = random.choice(self.watching_options)
                case "Playing":
                    name = random.choice(self.playing_options)
                case _:
                    name = "default"

            new_activity["name"] = name

        activity = discord.Activity(**new_activity)
        await self.bot.change_presence(activity=activity)

    @activity_changer.before_loop
    async def before_activity_changer(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
