import datetime
import json
import os

import discord
from discord.ext import tasks, commands

from discordbot.constants import CREATOR, BETA_USERS
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets


class EddieGainMessager(commands.Cog):
    def __init__(self, bot: discord.Client, guilds):
        self.bot = bot
        self.guilds = guilds
        self.eddie_distributer.start()

    def cog_unload(self):
        self.eddie_distributer.cancel()

    @tasks.loop(minutes=10)
    async def eddie_distributer(self):
        """
        Loop that takes all our active bets and ensures they haven't expired.
        :return:
        """
        path = os.path.join(os.path.expanduser("~"), "eddies_gained.json")
        if not os.path.exists(path):
            return

        with open(path) as f:
            eddie_dict = json.load(f)  # type: dict

        guild_id = eddie_dict.pop("guild")
        guild = self.bot.get_guild(guild_id)  # type: discord.Guild

        msg = f"Eddie gain summary:\n"
        for user_id in eddie_dict:
            msg += f"\n- `{user_id}`  :  **{eddie_dict[user_id]}**"
            if int(user_id) not in BETA_USERS:
                continue

            text = f"Yesterday, you gained `{eddie_dict[user_id]}` BSEDDIES!!"

            user = await guild.fetch_member(int(user_id))
            await user.send(content=text)

        user = await guild.fetch_member(CREATOR)  # type: discord.Member
        await user.send(content=msg)

        os.remove(path)

    @eddie_distributer.before_loop
    async def before_eddie_distributer(self):
        await self.bot.wait_until_ready()
