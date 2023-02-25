import datetime
import math
import random

import discord
from discord.ext import tasks, commands

from apis.giphyapi import GiphyAPI
from discordbot.bot_enums import SupporterType, TransactionTypes
from discordbot.constants import BSEDDIES_KING_ROLES, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.embedmanager import EmbedManager
from discordbot.views import RevolutionView
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from mongo.datatypes import RevolutionEventType


class BSEddiesRevolutionTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger, giphy_token, startup_tasks):
        self.bot = bot
        self.user_points = UserPoints()
        self.revolutions = RevolutionEvent()
        self.embed_manager = EmbedManager(logger)
        self.logger = logger
        self.startup_tasks = startup_tasks
        self.guild_ids = guilds
        self.guilds = Guilds()
        self.giphy_api = GiphyAPI(giphy_token)
        self.rev_started = False
        self.revolution.start()

        for guild_id in self.guild_ids:
            if _ := self.revolutions.get_open_events(guild_id):
                self.rev_started = True

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.revolution.cancel()

    def _check_start_up_tasks(self) -> bool:
        """
        Checks start up tasks
        """
        for task in self.startup_tasks:
            if not task.finished:
                return False
        return True

    @tasks.loop(minutes=1)
    async def revolution(self):
        """
        Constantly checks to make sure that all events have been closed properly or raised correctly
        :return:
        """
        if not self._check_start_up_tasks():
            self.logger.info("Startup tasks not complete - skipping loop")
            return

        now = datetime.datetime.now()

        if not self.rev_started and (now.weekday() != 6 or now.hour != 16 or now.minute != 0):
            return

        for guild in self.bot.guilds:
            guild_db = self.guilds.get_guild(guild.id)
            king_user = self.user_points.find_user(guild_db["king"], guild.id)

            user_points = king_user["points"]

            if not self.rev_started:
                # only trigger if King was King for more than twenty four hours
                king_since = guild_db.get("king_since", datetime.datetime.now() - datetime.timedelta(days=1))
                if (now - king_since).total_seconds() < 86400:
                    # user hasn't been king for more than twenty four hours
                    channel = await guild.fetch_channel(guild_db["channel"])
                    await channel.send(
                        content=(
                            f"<@{guild_db['king']}> has been <@&{guild_db['role']}> for less than **24** hours. "
                            "There will be no revolution today."
                        )
                    )
                    return

                event = self.revolutions.create_event(
                    guild.id,
                    datetime.datetime.now(),
                    datetime.datetime.now() + datetime.timedelta(hours=3, minutes=30),
                    king_user["uid"],
                    user_points,
                    guild.id
                )
            else:
                try:
                    event = self.revolutions.get_open_events(guild.id)[0]
                except IndexError:
                    # this guild doesn't have an open event so let's skip for now
                    continue

            self.rev_started = True

            message = event.get("message_id")
            if message is None:
                await self.create_event(guild.id, event)
                continue

            if now > event["expired"]:
                await self.resolve_revolution(guild.id, event)
                self.logger.info("Changing revolution task interval to 30 minutes.")
                continue

            elif now.hour == 18 and now.minute == 30 and not event.get("one_hour"):
                await self.send_excited_gif(event, "One hour", "one_hour")

            elif now.hour == 19 and now.minute == 15 and not event.get("quarter_house"):
                await self.send_excited_gif(event, "15 MINUTES", "quarter_hour")

    async def send_excited_gif(self, event: RevolutionEventType, hours_string: str, key: str):
        """
        Method for sending a countdown gif in regards to tickets and things
        :param guild.id:
        :param event:
        :param hours_string:
        :param key:
        :return:
        """
        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
        _message = await channel.fetch_message(event["message_id"])
        await channel.trigger_typing()
        gif = await self.giphy_api.random_gif("celebrate")
        await _message.send(
            content=f"Just under **{hours_string.upper()}** to go now - remember to choose your side!️"
        )
        await channel.send(content=gif)
        self.revolutions.update({"_id": event["_id"]}, {"$set": {key: True}})

    async def create_event(self, guild_id: int, event: RevolutionEventType):
        """
        Handle event creation - this takes a DB entry and posts the message into the channel.

        We also set the Channel ID and the Message ID for the
        :param guild.id:
        :param event:
        :return:
        """
        king_id = self.guilds.get_king(guild_id)

        king = await self.bot.fetch_user(king_id)  # type: discord.User
        guild_obj = await self.bot.fetch_guild(guild_id)  # type: discord.Guild
        role = guild_obj.get_role(BSEDDIES_KING_ROLES[guild_id])  # type: discord.Role
        channel = await self.bot.fetch_channel(BSEDDIES_REVOLUTION_CHANNEL)
        await channel.trigger_typing()

        revolution_view = RevolutionView(self.bot, event, self.logger)

        message = self.embed_manager.get_revolution_message(king, role, event, guild_obj)
        message_obj = await channel.send(content=message, view=revolution_view)  # type: discord.Message

        self.revolutions.update(
            {"_id": event["_id"]}, {"$set": {"message_id": message_obj.id, "channel_id": message_obj.channel.id}}
        )

        gif = await self.giphy_api.random_gif("revolution")
        await channel.send(content=gif)

    async def resolve_revolution(self, guild_id: int, event: RevolutionEventType):
        """
        Method for handling an event that needs resolving.

        We take the event chance and see if we generate a number between 0-100 that's lower than it. If it is, then
        we "win", otherwise we "lose". We handle both those conditions here too.
        :param guild.id:
        :param event:
        :return:
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

        self.rev_started = False

        if not _users:
            message = "No-one supported or overthrew the King - nothing happens."
            await channel.send(content=message)
            self.revolutions.close_event(event["event_id"], guild_id, False, 0)
            return

        val = (random.random() * 100)
        # cap and min chance so that each side _could_ always win
        chance = max(min(chance, 95), 5)
        success = val <= chance

        self.logger.debug(f"Number was: {val} and chance was: {chance}")
        points_to_lose = 0

        if not success:
            # revolution FAILED
            message = "Sadly, our revolution has failed. THE KING LIVES :crown: Better luck next week!"

            self.user_points.append_to_transaction_history(
                king_id, guild_id,
                {
                    "type": TransactionTypes.REV_TICKET_KING_WIN,
                    "event_id": event["event_id"],
                    "timestamp": datetime.datetime.now(),
                    "comment": "User survived a REVOLUTION",
                }
            )
            gif = await self.giphy_api.random_gif("disappointed")

        else:
            king_dict = self.user_points.find_user(king_id, guild_id, projection={"points": True})
            points_to_lose = math.floor(event.get("locked_in_eddies", king_dict["points"]) / 2)

            total_points_to_distribute = points_to_lose
            for supporter in supporters:
                supporter_eddies = self.user_points.get_user_points(supporter, guild_id)
                supporter_eddies_to_lose = math.floor(supporter_eddies * 0.1)
                total_points_to_distribute += supporter_eddies_to_lose
                self.user_points.decrement_points(supporter, guild_id, supporter_eddies_to_lose)
                self.user_points.append_to_transaction_history(
                    supporter, guild_id,
                    {
                        "type": TransactionTypes.SUPPORTER_LOST_REVOLUTION,
                        "amount": supporter_eddies_to_lose * -1,
                        "event_id": event["event_id"],
                        "timestamp": datetime.datetime.now(),
                        "comment": "Supporter lost a revolution",
                    }
                )

            points_each = math.floor(total_points_to_distribute / len(revolutionaries))

            message = (f"SUCCESS! THE KING IS DEAD! We have successfully taken eddies away from the KING. "
                       f"<@{king_id}> will lose **{points_to_lose}** and each of their supporters has lost"
                       f"`10%` of their eddies. Each revolutionary will gain `{points_each}` eddies.")

            self.user_points.decrement_points(king_id, guild_id, points_to_lose)
            self.user_points.append_to_transaction_history(
                king_id, guild_id,
                {
                    "type": TransactionTypes.REV_TICKET_KING_LOSS,
                    "amount": points_to_lose * -1,
                    "event_id": event["event_id"],
                    "timestamp": datetime.datetime.now(),
                    "comment": "King lost a REVOLUTION",
                }
            )

            gif = await self.giphy_api.random_gif("celebrate")

            for user_id in revolutionaries:
                self.user_points.increment_points(user_id, guild_id, points_each)
                self.user_points.append_to_transaction_history(
                    user_id, guild_id,
                    {
                        "type": TransactionTypes.REV_TICKET_WIN,
                        "amount": points_each,
                        "event_id": event["event_id"],
                        "timestamp": datetime.datetime.now(),
                        "comment": "User won a REVOLUTION",
                    }
                )

        # reset those that pledged to support - users can now _not_ support if they want
        self.guilds.reset_pledges(guild_id)

        # do roles

        supporter_role = guild.get_role(guild_db["supporter_role"])  # type: discord.Role
        revo_role = guild.get_role(guild_db["revolutionary_role"])

        # clear anyone that has the role already
        for member in supporter_role.members:
            if member.id not in supporters or success:
                # only remove if the king was removed _or_ they didn't support
                await member.remove_roles(supporter_role)

        for member in revo_role.members:
            if member.id not in revolutionaries:
                await member.remove_roles(revo_role)

        # supporters get Supporter role
        supporter_type = SupporterType.SUPPORTER
        for supporter in supporters:
            supporter_guild = await guild.fetch_member(supporter)
            if supporter_role not in supporter_guild.roles:
                await supporter_guild.add_roles(supporter_role)
            self.user_points.update({"uid": supporter}, {"$set": {"supporter_type": supporter_type}})

        # revolutonaries get revolutionary role

        for revolutionary in revolutionaries:
            revolutionary_guild = await guild.fetch_member(revolutionary)
            if revo_role not in revolutionary_guild.roles:
                await revolutionary_guild.add_roles(revo_role)

        await _message.edit(content=_message.content, view=None)
        await _message.reply(content=message)
        await channel.send(content=gif)
        self.revolutions.close_event(event["event_id"], guild_id, success, points_to_lose)

    @revolution.before_loop
    async def before_revolution(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
