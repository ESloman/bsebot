import datetime
import random

from discord.ext import tasks, commands

from discordbot.bsebot import BSEBot
from discordbot.constants import VALORANT_CHAT, VALORANT_ROLE, BSE_SERVER_ID, BSE_BOT_ID
from mongo.bsepoints.interactions import UserInteractions


class AfterWorkVally(commands.Cog):
    def __init__(self, bot: BSEBot, guilds, logger, startup_tasks):
        self.bot = bot
        self.logger = logger
        self.guilds = guilds
        self.startup_tasks = startup_tasks
        self.user_interactions = UserInteractions()
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
            "Balls. {role}"
        ]

    def _check_start_up_tasks(self) -> bool:
        """
        Checks start up tasks
        """
        for task in self.startup_tasks:
            if not task.finished:
                return False
        return True

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
        if not self._check_start_up_tasks():
            self.logger.info("Startup tasks not complete - skipping loop")
            return

        if BSE_SERVER_ID not in self.guilds:
            return

        now = datetime.datetime.now()

        if now.weekday() not in [0, 1, 2, 3, 4]:
            return

        if now.hour != 15 or not (45 <= now.minute <= 54):
            return

        self.logger.info("Checking for channel interactivity")

        latest_bot_message = list(self.user_interactions.vault.find(
            {"user_id": BSE_BOT_ID, "channel_id": VALORANT_CHAT, "message_type": "role_mention"},
            sort=[("timestamp", -1)],
            limit=1
        ))[0]

        latest_time = latest_bot_message["timestamp"]

        messages = self.user_interactions.query(
            {
                "timestamp": {"$gt": latest_time},
                "channel_id": VALORANT_CHAT
            }
        )

        if not messages:
            self.logger.info(
                f"Not been any messages in #valorant-chat since {latest_time} - skipping the daily vally message"
            )
            return

        self.logger.debug(f"{len(messages)} since our last vally rollcall")

        self.logger.info("Time to send vally message!")

        guild = await self.bot.fetch_guild(BSE_SERVER_ID)  # type: discord.Guild
        channel = await self.bot.fetch_channel(VALORANT_CHAT)
        await channel.trigger_typing()
        role = guild.get_role(VALORANT_ROLE)

        message = random.choice(self.messages)  # type: str
        message = message.format(role=role.mention)

        self.logger.info(f"Sending daily vally message: {message}")
        await channel.send(content=message)

    @vally_message.before_loop
    async def before_vally_message(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
