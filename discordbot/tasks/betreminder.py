
import asyncio
import datetime
from logging import Logger

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask


class BetReminder(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
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
        for guild in self.bot.guilds:
            await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild.id)
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
                    channel = await self.bot.fetch_channel(bet["channel_id"])
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
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
