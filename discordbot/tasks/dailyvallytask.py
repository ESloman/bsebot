
import asyncio
import datetime
import random
from logging import Logger

from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.constants import BSE_SERVER_ID
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
        self.vally_message.start()

        self.messages = [
            "Anyone playing after-work {role} today?",
            "Who's about for after-work {role}?",
            "Anyone wanna get salty playing {role}?",
            "Who's gonna grind some `Lotus` today {role}?",
            "Anyone want to lose some RR {role}?",
            "Who wants to roll some fat 1s playing {role}?",
            "Can we get an after-work 5-stack today for {role}?",
            "My pp is soft, but my Valorant is hard. Someone play a game with me, {role}?",
            "Jingle bells, jingle bells, jingle all the IT'S TIME TO PLAY VALORANT {role}",
            "Valorant? Valorant? VALORANT? VALROARANT? RAVALROANT? {role}",
            "I'm a little bot, it's time to get mad and play {role}?",
            "# Balls. {role}"
        ]

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.vally_message.cancel()

    @tasks.loop(minutes=10)
    async def vally_message(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
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

            message = random.choice(self.messages)
            message = message.format(role=_mention)

            self.logger.info(f"Sending daily vally message: {message}")
            await channel.send(content=message)

    @vally_message.before_loop
    async def before_vally_message(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
