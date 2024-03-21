"""Revolution bribe task."""

import datetime
from logging import Logger
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from discordbot.views.revolutionbribeview import RevolutionBribeView
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.revolution import RevolutionEventDB

BRIBE_THRESHOLD = 60
MAX_TIME_KING_THRESHOLD = 2.628e6


class RevolutionBribeTask(BaseTask):
    """Class for our revolution bribe task."""

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        start: bool = False,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            start (bool): whether to start the task at startup. Default to False.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.schedule = TaskSchedule([6], [19], minute=1)
        self.task = self.bribe
        if start:
            self.task.start()

    def _get_king_times(self, guild: discord.Guild) -> dict[int, float]:
        """Gets everyone's total time King.

        Args:
            guild (discord.Guild): the guild to check

        Returns:
            dict[int, float]: the dict of user IDs to total time King
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        start = now.replace(year=2021, month=1, day=1)
        activity_history = self.activities.get_guild_activities_by_timestamp(guild.id, start, now)
        king_events = sorted(
            [act for act in activity_history if act.type in {ActivityTypes.KING_GAIN, ActivityTypes.KING_LOSS}],
            key=lambda x: x.timestamp,
        )

        kings: dict[int, float] = {}
        previous_time = start

        for event in king_events:
            if event.type == ActivityTypes.KING_LOSS:
                if previous_time is None:
                    continue
                time_king = (event.timestamp - previous_time).total_seconds()

                if event.uid not in kings:
                    kings[event.uid] = 0
                kings[event.uid] += time_king
                previous_time = None

            elif event.type == ActivityTypes.KING_GAIN:
                previous_time = event.timestamp

        if king_events[-1] == event and event.type == ActivityTypes.KING_GAIN:
            # last thing someone did was become KING
            time_king = (now - event.timestamp).total_seconds()
            if event.uid not in kings:
                kings[event.uid] = 0
            kings[event.uid] += time_king

        return kings

    def _check_guild_bribe_conditions(self, guild_db: GuildDB, open_events: list[RevolutionEventDB]) -> bool:
        if not guild_db.revolution:
            self.logger.debug("Revolution not enabled for %s - no need to bribe.", guild_db.name)
            return False

        open_events = self.revolutions.get_open_events(guild_db.guild_id)
        if not open_events:
            self.logger.debug("No open events for %s to bribe", guild_db.name)
            return False

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        time_king: float = (now - guild_db.king_since).total_seconds()

        if time_king >= MAX_TIME_KING_THRESHOLD:
            self.logger.debug("King has been King long enough - not bribing.")
            return False

        return True

    def _check_event_bribe_conditions(self, event: RevolutionEventDB) -> bool:
        if event.chance < BRIBE_THRESHOLD:
            self.logger.debug("Event chance is too low (%s) - not bribing.", event.chance)
            return False

        if event.times_saved:
            self.logger.debug("King has already tried to save themself %s times - not bribing.")
            return False
        return True

    def _check_bribe_conditions(self, guild: discord.Guild) -> bool:
        guild_db = self.guilds.get_guild(guild.id)
        open_events = self.revolutions.get_open_events(guild_db.guild_id)

        if not self._check_guild_bribe_conditions(guild_db, open_events):
            return False

        event = open_events[0]

        if not self._check_event_bribe_conditions(event):
            return False

        users = self.user_points.get_all_users_for_guild(guild.id, {"points": True})
        users = sorted(users, key=lambda user: user.points, reverse=True)

        if users[0].uid != guild_db.king:
            self.logger.debug("King won't be King after the revolution - not bribing.")
            return False

        # king user
        king = users[0]
        # person in line to be king
        in_line = users[1]

        # save thyself cost
        save_cost = king.points * 0.1
        if (king.points - in_line.points) >= save_cost:
            self.logger.debug("King has enough points to save themself - not bribing.")
            return False

        king_times = self._get_king_times(guild)
        sorted_kings = sorted(king_times, key=lambda x: king_times[x], reverse=True)
        position = sorted_kings.index(guild_db.king)

        if position in {0, 1}:
            self.logger.debug("King is position %s for total King time - not bribing.", position)
            return False

        return True

    @tasks.loop(count=1)
    async def bribe(self) -> None:
        """Our revolution task.

        Creates a revolution event weekly and then handles the
        closing/resolving of that event.
        """
        for guild in self.bot.guilds:
            guild_db = self.guilds.get_guild(guild.id)

            if not self._check_bribe_conditions(guild):
                continue

            # we meet the condition for a bribe!
            open_events = self.revolutions.get_open_events(guild_db.guild_id)
            event = open_events[0]
            king_user = self.user_points.find_user(guild_db.king, guild_db.guild_id)

            users = self.user_points.get_all_users_for_guild(guild.id, {"points": True})
            users = sorted(users, key=lambda user: user.points, reverse=True)

            in_line_user = users[1]
            bribe_cost = round((king_user.points - in_line_user.points) / 2)
            self.logger.debug("Got bribe cost for %s - %s to be: %s", guild_db.name, king_user.name, bribe_cost)

            bribe_message = self.embed_manager.get_revolution_bribe_message(guild_db, event, king_user, bribe_cost)

            self.logger.debug("Bribe message: %s", bribe_message)
            self.logger.debug("Bribe message is %s chars long.", len(bribe_message))

            view = RevolutionBribeView(self.bot, event, self.logger)
            member = await guild.fetch_member(king_user.uid)
            try:
                await member.send(content=bribe_message, view=view)
                self.revolutions.set_bribe_offered_flag(event.event_id)
                self.logger.info("Sent bribe message to %s.", king_user.name)
            except discord.errors.Forbidden:
                # not allowed to send dms - oh well
                self.logger.warning("Was unable to bribe %s due to not allowing DMs.", king_user.name)
