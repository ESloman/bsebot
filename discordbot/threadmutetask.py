import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID, GENERAL_CHAT
from mongo.bsedataclasses import SpoilerThreads


class ThreadSpoilerTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.spoilers = SpoilerThreads()

        self.thread_mute.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.thread_mute.cancel()

    @tasks.loop(minutes=15)
    async def thread_mute(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        now = datetime.datetime.now()
        if now.hour != 8 and not (0 <= now.minute < 15):
            return

        if BSE_SERVER_ID not in self.guilds:
            return

        print(f"Checking spoiler threads for mute messages")
        guild = await self.bot.fetch_guild(BSE_SERVER_ID)
        general = await guild.fetch_channel(GENERAL_CHAT)
        threads = general.threads

        if not threads:
            # no threads
            return

        for thread in general.threads:
            if "spoiler" not in thread.name.lower():
                continue

            thread_id = thread.id
            thread_info = self.spoilers.get_thread_by_id(BSE_SERVER_ID, thread_id)

            if not thread_info:
                print(f"No info for thread {thread_id}, {thread.name}")
                continue

            day = thread_info["day"]
            if now.weekday() != day:
                # not the right day for this spoiler thread
                continue

            message = f"New episode today - remember to mute cuties @everyone xoxo"
            await thread.send(content=message, allowed_mentions=discord.AllowedMentions(everyone=True))

    @thread_mute.before_loop
    async def before_thread_mute(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
