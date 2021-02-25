import datetime

import discord
from discord.ext import tasks, commands

from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserBets


class BetCloser(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.guilds = guilds
        self.user_bets = UserBets()
        self.logger = logger
        self.embed_manager = EmbedManager(self.logger)
        self.bet_closer.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.bet_closer.cancel()

    @tasks.loop(seconds=10.0)
    async def bet_closer(self):
        """
        Loop that takes all our active bets and ensures they haven't expired.
        If they have expired - they get closed.
        :return:
        """
        now = datetime.datetime.now()
        for guild in self.guilds:
            guild_obj = self.bot.get_guild(guild)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild)
            for bet in active:
                if timeout := bet.get("timeout"):
                    if timeout < now:
                        # set the bet to no longer active ??
                        self.user_bets.update({"_id": bet["_id"]}, {"$set": {"active": False}})
                        member = guild_obj.get_member(bet["user"])
                        channel = guild_obj.get_channel(bet["channel_id"])
                        message = await channel.fetch_message(bet["message_id"])  # type: discord.Message
                        bet["active"] = False
                        embed = self.embed_manager.get_bet_embed(guild_obj, bet["bet_id"], bet)
                        await message.edit(embed=embed)
                        msg = (f"Your bet `{bet['bet_id']} - {bet['title']}` (<{message.jump_url}>) "
                               f"is now closed for bets and is waiting a result from you.")
                        if not member.dm_channel:
                            await member.create_dm()
                        try:
                            await member.send(content=msg)
                        except discord.errors.Forbidden:
                            pass

    @bet_closer.before_loop
    async def before_bet_closer(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
