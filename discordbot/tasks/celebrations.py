import datetime

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL


class Celebrations(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.celebrations.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.celebrations.cancel()

    @tasks.loop(minutes=15)
    async def celebrations(self):
        """
        Send celebration message
        :return:
        """
        now = datetime.datetime.now()

        if BSE_SERVER_ID not in self.guilds:
            return

        if now.month == 12 and now.day == 25:
            # christmas day!!
            if now.hour != 8 or not (15 <= now.minute < 30):
                # already in christmas day - can exit func safely
                return
            # now we can send message!
            msg = "Merry Christmas to my favourite server ❤️🎄"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 1 and now.day == 1:
            # new years day!!
            if now.hour != 0 or not (0 <= now.minute < 15):
                # already in NY so we can exit func safely
                return
            # now we can send message!
            msg = f"Happy New Year! May you be blessed with many eddies in {now.year}! 🎆🎉💋"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 2 and now.day == 11:
            # my birthday!!
            if now.hour != 10 or not (0 <= now.minute < 15):
                # already in birthday so can exit func safely
                return
            birth_year = self.bot.user.created_at.year
            age = now.year - birth_year
            msg = f"It's my birthday today and I am `{age}` years old! 🍰🧁"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

        if now.month == 5 and now.day == 14:
            # BSE birthday
            if now.hour != 10 or not (0 <= now.minute < 15):
                # already in birthday so can exit func safely
                return
            bse_created_year = 2016
            age = now.year - bse_created_year
            msg = f"Happy birthday to **Best Summer Ever**! {age} years old today! 🍰🎆🎉"
            channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
            await channel.trigger_typing()
            await channel.send(content=msg)
            return

    @celebrations.before_loop
    async def before_celebrations(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
