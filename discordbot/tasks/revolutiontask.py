"""Revolution task."""

import asyncio
import datetime
import math
import random
from logging import Logger

from discord.ext import tasks

from apis.giphyapi import GiphyAPI
from discordbot.bot_enums import SupporterType, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.tasks.basetask import BaseTask
from discordbot.views.revolution import RevolutionView
from mongo.datatypes import GuildDB, RevolutionEventType


class BSEddiesRevolutionTask(BaseTask):
    """Class for our revolution task."""

    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        giphy_token: str,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.revolution
        self.embed_manager = EmbedManager(logger)
        self.giphy_api = GiphyAPI(giphy_token)
        self.rev_started = {}

        for guild_id in self.guild_ids:
            if _ := self.revolutions.get_open_events(guild_id):
                self.rev_started[guild_id] = True

        self.task.start()

    @tasks.loop(minutes=1)
    async def revolution(self) -> None:  # noqa: C901, PLR0912
        """Our revolution task.

        Creates a revolution event weekly and then handles the
        closing/resolving of that event.
        """
        if not self._check_start_up_tasks():
            self.logger.info("Startup tasks not complete - skipping loop")
            return

        now = datetime.datetime.now()

        if not any(self.rev_started[g] for g in self.rev_started) and (
            now.weekday() != 6 or now.hour != 16 or now.minute != 0  # noqa: PLR2004
        ):
            return

        for guild in self.bot.guilds:
            guild_db = self.guilds.get_guild(guild.id)

            if guild_db.revolution is False:
                # revolution event has been disabled
                if now.hour == 16 and now.minute == 0:  # noqa: PLR2004
                    # only log once per revolution event that this guild is disabled
                    self.logger.debug("Revolution event has been disabled for %s", guild.name)
                continue

            king_user = self.user_points.find_user(guild_db.king, guild.id)

            user_points = king_user.points

            # if we don't have an actual revolution event and it IS 4PM then we trigger a new event
            if not self.rev_started.get(guild.id) and now.hour == 16 and now.minute == 0:  # noqa: PLR2004
                # only trigger if King was King for more than twenty four hours
                king_since = guild_db.get("king_since", datetime.datetime.now() - datetime.timedelta(days=1))
                if (now - king_since).total_seconds() < 86400:  # noqa: PLR2004
                    # user hasn't been king for more than twenty four hours
                    channel = await self.bot.fetch_channel(guild_db.channel)
                    await channel.send(
                        content=(
                            f"<@{guild_db.king}> has been <@&{guild_db.role}> for less than **24** hours. "
                            "There will be no revolution today."
                        ),
                        silent=True,
                    )
                    return

                event = self.revolutions.create_event(
                    guild.id,
                    datetime.datetime.now(),
                    datetime.datetime.now() + datetime.timedelta(hours=3, minutes=30),
                    king_user.uid,
                    user_points,
                    guild_db.channel,
                )
            else:
                try:
                    event = self.revolutions.get_open_events(guild.id)[0]
                except IndexError:
                    # this guild doesn't have an open event so let's skip for now
                    continue

            self.rev_started[guild.id] = True

            message = event.get("message_id")
            if message is None:
                await self.create_event(guild.id, event, guild_db)
                continue

            if now > event["expired"]:
                await self.resolve_revolution(guild.id, event)
                self.logger.info("Changing revolution task interval to 30 minutes.")
                continue

            if now.hour == 18 and now.minute == 30 and not event.get("one_hour"):  # noqa: PLR2004
                await self.send_excited_gif(event, "One hour", "one_hour")

            elif now.hour == 19 and now.minute == 15 and not event.get("quarter_house"):  # noqa: PLR2004
                await self.send_excited_gif(event, "15 MINUTES", "quarter_hour")

    async def send_excited_gif(self, event: RevolutionEventType, hours_string: str, key: str) -> None:
        """Method for sending a countdown gif in regards to tickets and things.

        Args:
            event (RevolutionEventType): the event
            hours_string (str): the text to send
            key (str): the key in the database to modify
        """
        channel = await self.bot.fetch_channel(event["channel_id"])
        _message = await channel.fetch_message(event["message_id"])
        await channel.trigger_typing()
        gif = await self.giphy_api.random_gif("celebrate")
        await _message.reply(content=f"Just under **{hours_string.upper()}** to go now - remember to choose your side!️")
        await channel.send(content=gif)
        self.revolutions.update({"_id": event["_id"]}, {"$set": {key: True}})

    async def create_event(self, guild_id: int, event: RevolutionEventType, guild_db: GuildDB) -> None:
        """Handle event creation - this takes a DB entry and posts the message into the channel.

        We also set the Channel ID and the Message ID for the event.

        Args:
            guild_id (int): the guild ID
            event (RevolutionEventType): the event
            guild_db (GuildDB): the guild database entry
        """
        king_id = self.guilds.get_king(guild_id)

        king = await self.bot.fetch_user(king_id)
        guild_obj = await self.bot.fetch_guild(guild_id)
        role = guild_obj.get_role(guild_db.role)
        channel = await self.bot.fetch_channel(guild_db.channel)
        await channel.trigger_typing()

        revolution_view = RevolutionView(self.bot, event, self.logger)

        message = self.embed_manager.get_revolution_message(king, role, event, guild_obj)
        message_obj = await channel.send(content=message, view=revolution_view)

        self.revolutions.update(
            {"_id": event["_id"]},
            {"$set": {"message_id": message_obj.id, "channel_id": message_obj.channel.id}},
        )

        gif = await self.giphy_api.random_gif("revolution")
        await channel.send(content=gif)

    async def resolve_revolution(self, guild_id: int, event: RevolutionEventType) -> None:  # noqa: C901, PLR0915, PLR0912
        """Method for handling an event that needs resolving.

        We take the event chance and see if we generate a number between 0-100 that's lower than it. If it is, then
        we "win", otherwise we "lose". We handle both those conditions here too.

        Args:
            guild_id (int): the guild ID
            event (RevolutionEventType): the event
        """
        chance = event["chance"]
        king_id = event.get("king", self.guilds.get_king(guild_id))
        _users = event["users"]
        revolutionaries = event["revolutionaries"]
        supporters = event["supporters"]
        channel_id = event["channel_id"]
        guild_db = self.guilds.get_guild(guild_id)

        guild = await self.bot.fetch_guild(guild_id)
        channel = await self.bot.fetch_channel(channel_id)
        _message = await channel.fetch_message(event["message_id"])

        await channel.trigger_typing()

        self.rev_started[guild_id] = False

        if not _users:
            message = "No-one supported or overthrew the King - nothing happens."
            await channel.send(content=message)
            self.revolutions.close_event(event["event_id"], guild_id, False, 0)
            return

        val = random.random() * 100
        # cap and min chance so that each side _could_ always win
        chance = max(min(chance, 95), 5)
        success = val <= chance

        self.logger.debug("Number was: %s and chance was: %s", val, chance)
        points_to_lose = 0

        if not success:
            # revolution FAILED
            message = "Sadly, our revolution has failed. THE KING LIVES :crown: Better luck next week!"
            gif = await self.giphy_api.random_gif("disappointed")
        else:
            king_dict = self.user_points.find_user(king_id, guild_id)
            points_to_lose = math.floor(event.get("locked_in_eddies", king_dict.points) / 2)

            total_points_to_distribute = points_to_lose
            for supporter in supporters:
                supporter_eddies = self.user_points.get_user_points(supporter, guild_id)
                supporter_eddies_to_lose = math.floor(supporter_eddies * 0.1)
                total_points_to_distribute += supporter_eddies_to_lose
                self.user_points.increment_points(
                    supporter,
                    guild_id,
                    supporter_eddies_to_lose * -1,
                    TransactionTypes.SUPPORTER_LOST_REVOLUTION,
                    event_id=event["event_id"],
                    comment="Supporter lost a revolution",
                )

            points_each = math.floor(total_points_to_distribute / len(revolutionaries))

            message = (
                f"SUCCESS! THE KING IS DEAD! We have successfully taken eddies away from the KING. "
                f"<@{king_id}> will lose **{points_to_lose}** and each of their supporters has lost"
                f"`10%` of their eddies. Each revolutionary will gain `{points_each}` eddies."
            )

            self.user_points.increment_points(
                king_id,
                guild_id,
                points_to_lose * -1,
                TransactionTypes.REV_TICKET_KING_LOSS,
                event_id=event["event_id"],
                comment="King lost a REVOLUTION",
            )

            gif = await self.giphy_api.random_gif("celebrate")

            for user_id in revolutionaries:
                self.user_points.increment_points(
                    user_id,
                    guild_id,
                    points_each,
                    TransactionTypes.REV_TICKET_WIN,
                    event_id=event["event_id"],
                    comment="User won a REVOLUTION",
                )

        # reset those that pledged to support - users can now _not_ support if they want
        self.guilds.reset_pledges(guild_id)

        # do roles

        supporter_role = guild.get_role(guild_db.supporter_role)
        revo_role = guild.get_role(guild_db.revolutionary_role)

        # clear anyone that has the role already
        for member in supporter_role.members:
            if member.id not in supporters or success:
                # only remove if the king was removed _or_ they didn't support
                await member.remove_roles(supporter_role)

        for member in revo_role.members:
            if member.id not in revolutionaries:
                await member.remove_roles(revo_role)

        # reset role names
        if success:
            # only when a KING was dethroned though
            if supporter_role.name != "Supporters":
                await supporter_role.edit(name="Supporters")
            if revo_role.name != "Revolutionaries":
                await revo_role.edit(name="Revolutionaries")

        # make everyone neutral
        self.user_points.update(
            {"guild_id": guild_id, "active": True},
            {"$set": {"supporter_type": SupporterType.NEUTRAL}},
            many=True,
        )

        # supporters get Supporter role
        supporter_type = SupporterType.SUPPORTER
        for supporter in supporters:
            supporter_guild = guild.get_member(supporter)
            if not supporter_guild:
                supporter_guild = await guild.fetch_member(supporter)
            if supporter_role not in supporter_guild.roles:
                await supporter_guild.add_roles(supporter_role)
            self.user_points.update(
                {"uid": supporter, "guild_id": guild_id},
                {"$set": {"supporter_type": supporter_type}},
            )

        # revolutonaries get revolutionary role
        if not success:
            supporter_type = SupporterType.REVOLUTIONARY
            for revolutionary in revolutionaries:
                revolutionary_guild = guild.get_member(revolutionary)
                if not revolutionary_guild:
                    revolutionary_guild = await guild.fetch_member(revolutionary)
                if revo_role not in revolutionary_guild.roles:
                    await revolutionary_guild.add_roles(revo_role)
                self.user_points.update(
                    {"uid": revolutionary, "guild_id": guild_id},
                    {"$set": {"supporter_type": supporter_type}},
                )

        await _message.edit(content=_message.content, view=None)
        await _message.reply(content=message)
        await channel.send(content=gif)
        self.revolutions.close_event(event["event_id"], guild_id, success, points_to_lose)
        # set last revolution time in the database
        self.guilds.update({"guild_id": guild_id}, {"$set": {"last_revolution_time": datetime.datetime.now()}})

    @revolution.before_loop
    async def before_revolution(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
