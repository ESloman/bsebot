
import asyncio
import datetime
import random
from logging import Logger

from discord.ext import tasks
from pymongo.errors import OperationFailure

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
from discordbot.message_strings.valorant_rollcalls import MESSAGES
from discordbot.tasks.basetask import BaseTask


class AfterWorkVally(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask]
    ):

        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.vally_message
        self.task.start()

    @tasks.loop(minutes=10)
    async def vally_message(self):
        """
        Loop that sends the daily vally rollcall
        """

        if BSE_SERVER_ID not in self.guild_ids:
            return

        now = datetime.datetime.now()

        if now.weekday() not in [0, 1, 2, 3, 4]:
            return

        if now.hour != 15 or not (45 <= now.minute <= 54):
            return

        for guild in self.bot.guilds:
            # set this up for theoretically working with other guilds
            # but only work for BSE Server for now
            if guild.id != BSE_SERVER_ID:
                continue

            guild_db = self.guilds.get_guild(guild.id)

            if not guild_db.get("valorant_rollcall"):
                self.logger.info("Valorant rollcall is disabled")
                continue

            valorant_channel = guild_db.get("valorant_channel")
            if not valorant_channel:
                self.logger.info("Valorant channel isn't configured")
                continue

            self.logger.info("Checking for channel interactivity")

            latest_bot_message = list(self.interactions.vault.find(
                {"user_id": self.bot.user.id, "channel_id": valorant_channel, "message_type": "role_mention"},
                sort=[("timestamp", -1)],
                limit=1
            ))[0]

            latest_time = latest_bot_message["timestamp"]

            messages = self.interactions.query(
                {
                    "timestamp": {"$gt": latest_time},
                    "channel_id": valorant_channel,
                    "is_bot": False,
                }
            )

            if not messages:
                self.logger.info(
                    f"Not been any messages in the channel since {latest_time} - skipping the daily vally message"
                )
                continue

            self.logger.debug(f"{len(messages)} since our last vally rollcall")
            self.logger.info("Time to send vally message!")

            guild = await self.bot.fetch_guild(guild.id)
            channel = await self.bot.fetch_channel(valorant_channel)
            await channel.trigger_typing()

            if role_id := guild_db.get("valorant_role"):
                role = guild.get_role(role_id)
                _mention = role.mention
            else:
                _mention = "`Valorant`"

            # work out message odds
            odds = []
            totals = {}
            # get the number of times each rollcall message has been used
            for message in MESSAGES:
                parts = message.split("{role}")
                main_bit = sorted(parts, key=lambda x: len(x), reverse=True)[0]

                try:
                    results = self.interactions.query(
                        {
                            "guild_id": guild.id,
                            "is_bot": True,
                            "$text": {"$search": message}
                        }
                    )
                    results = [result for result in results if main_bit in result["content"]]
                except OperationFailure:
                    totals[message] = 0
                    continue

                totals[message] = len(results)

            # work out the weight that a given message should be picked
            total_rollcalls = sum(totals.values())
            for message in MESSAGES:
                _times = totals[message]
                _chance = (1 - (_times / total_rollcalls)) * 100

                # give greater weighting to standard messages
                if MESSAGES.index(message) in [0, 1]:
                    _chance += 25

                # give greater weighting to those with 0 uses so far
                if _times == 0:
                    _chance += 25

                odds.append((message, _chance))

            message = random.choices([message[0] for message in totals], [message[1] for message in totals])
            message = message.format(role=_mention)

            self.logger.info(f"Sending daily vally message: {message}")
            await channel.send(content=message)

    @vally_message.before_loop
    async def before_vally_message(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
