import datetime
import random
import re

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID, GENERAL_CHAT
from mongo.bsepoints import UserInteractions


class WordleTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.wordle_message.start()
        self.user_interactions = UserInteractions()
        self.set_wordle_activity = False
        self.sent_wordle = False
        self.wait_iters = None

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.vally_message.cancel()

    @tasks.loop(minutes=15)
    async def wordle_message(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        now = datetime.datetime.now()

        if now.hour < 7:
            self.sent_wordle = False
            self.set_wordle_activity = False
            return

        if self.sent_wordle and not self.set_wordle_activity:
            return

        if now.hour > 9:
            if self.set_wordle_activity:
                listening_activity = discord.Activity(
                    name="conversations",
                    state="Listening",
                    type=discord.ActivityType.listening,
                    details="Waiting for commands!"
                )
                await self.bot.change_presence(activity=listening_activity, status=discord.Status.idle)
                self.set_wordle_activity = False
            return

        if self.sent_wordle:
            return

        if not self.set_wordle_activity:
            game = discord.Game("Wordle")
            await self.bot.change_presence(status=discord.Status.online, activity=game)
            self.set_wordle_activity = True

        if self.wait_iters is None:
            self.wait_iters = random.randint(0, 2)
            return

        if self.wait_iters != 0:
            self.wait_iters -= 1
            return

        # wait iters is 0
        assert self.wait_iters == 0

        # actually do wordle now

        earlier = now.replace(hour=0, minute=0, second=1)

        wordles_today = self.user_interactions.query(
            {
                "guild_id": BSE_SERVER_ID,
                "timestamp": {"$gt": earlier},
                "message_type": "wordle"
            }
        )

        if not wordles_today:
            # couldn't find any today yet
            earlier = earlier - datetime.timedelta(days=1)
            wordles_yesterday = self.user_interactions.query(
                {
                    "guild_id": BSE_SERVER_ID,
                    "timestamp": {"$gt": earlier},
                    "message_type": "wordle"
                }
            )
            first = wordles_yesterday[0]
            content = first["content"]
            _match = re.match(r"Wordle \d+", content)
            value = int(_match.group().split()[1]) + 1

        else:
            first = wordles_today[0]
            content = first["content"]
            _match = re.match(r"Wordle \d+", content)
            value = _match.group().split()[1]

        print(f"Got wordle number to be: {value}")

        random_wordle = list(self.user_interactions.vault.aggregate([
            {"$match": {"message_type": "wordle"}},
            {"$sample": {"size": 1}}
        ]
        ))[0]
        content = random_wordle["content"]
        message = re.sub(r"(?<= )\d+(?= )", f"{value}", content)

        guild = await self.bot.fetch_guild(BSE_SERVER_ID)
        channel = await guild.fetch_channel(GENERAL_CHAT)

        print(f"Sending wordle message: {message}")
        await channel.send(content=message)
        self.sent_wordle = True

        listening_activity = discord.Activity(
            name="conversations",
            state="Listening",
            type=discord.ActivityType.listening,
            details="Waiting for commands!"
        )
        await self.bot.change_presence(activity=listening_activity, status=discord.Status.idle)
        self.set_wordle_activity = False

    @wordle_message.before_loop
    async def before_wordle_message(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
