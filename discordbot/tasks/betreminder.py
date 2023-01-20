import datetime

import discord
from discord.ext import tasks, commands

from mongo.bsepoints import UserBets


class BetReminder(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.guilds = guilds
        self.user_bets = UserBets()
        self.logger = logger
        self.bet_reminder.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.bet_reminder.cancel()

    @tasks.loop(minutes=60)
    async def bet_reminder(self):
        """
        Loop that takes all our active bets and sends a reminder message
        :return:
        """
        now = datetime.datetime.now()
        for guild in self.guilds:
            guild_obj = self.bot.get_guild(guild)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild)
            for bet in active:
                timeout = bet["timeout"]
                created = bet["created"]
                if (timeout - created).total_seconds() <= 172800:
                    continue

                if now > timeout:
                    continue

                diff = timeout - now
                if 82800 <= diff.total_seconds() <= 86400:
                    # ~ 24 hours to go!
                    # send reminder here
                    channel = await guild_obj.fetch_channel(bet["channel_id"])
                    await channel.trigger_typing()
                    message = await channel.fetch_message(bet["message_id"])

                    num_betters = len(bet["betters"].keys())
                    eddies_bet = self.user_bets.count_eddies_for_bet(bet)

                    msg = (
                        "Only roughly twenty four hours to get in on this bet!\n"
                        f"Current there's `{eddies_bet}` eddies on the line from **{num_betters}** betters."
                    )
                    await message.reply(content=msg)

    @bet_reminder.before_loop
    async def before_bet_reminder(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
