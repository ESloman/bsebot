import datetime
import math
import random

import discord
from discord.ext import tasks, commands

from apis.giphyapi import GiphyAPI
from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BSEDDIES_KING_ROLES, BSEDDIES_REVOLUTION_CHANNEL
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserPoints
from mongo.bseticketedevents import RevolutionEvent


class BSEddiesRevolutionTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger, giphy_token):
        self.bot = bot
        self.user_points = UserPoints()
        self.revolutions = RevolutionEvent()
        self.embed_manager = EmbedManager(logger)
        self.logger = logger
        self.guilds = guilds
        self.giphy_api = GiphyAPI(giphy_token)
        self.revolution.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.revolution.cancel()

    @tasks.loop(minutes=5)
    async def revolution(self):
        """
        Constantly checks to make sure that all events have been closed properly or raised correctly
        :return:
        """
        now = datetime.datetime.now()

        if now.weekday() == 6 and self.revolution.hours == 8:
            self.logger.info("Changing revolution task interval to 15 minutes.")
            self.revolution.change_interval(minutes=15, hours=0)
        elif now.weekday() != 6 and self.revolution.hours != 8:
            self.logger.info("Changing revolution task interval back to 8 hours.")
            self.revolution.change_interval(hours=8, minutes=0)

        for guild_id in self.guilds:

            open_events = self.revolutions.get_open_events(guild_id)
            for event in open_events:

                message = event.get("message_id")
                if message is None:
                    await self.create_event(guild_id, event)
                    self.logger.info("Changing revolution task interval to 5 minutes.")
                    self.revolution.change_interval(minutes=5)
                    continue

                if now > event["expired"]:
                    await self.handle_resolving_bet(guild_id, event)
                    self.logger.info("Changing revolution task interval to 30 minutes.")
                    self.revolution.change_interval(minutes=30)
                    continue

                if (event["expired"] - now).total_seconds() < 10800 and not event.get("three_hours"):
                    await self.send_excited_gif(guild_id, event, "Three hours", "three_hours")

                elif (event["expired"] - now).total_seconds() < 7200 and not event.get("two_hours"):
                    await self.send_excited_gif(guild_id, event, "Two hours", "two_hours")

                elif (event["expired"] - now).total_seconds() < 3600 and not event.get("one_hour"):
                    await self.send_excited_gif(guild_id, event, "One hour", "one_hour")

                elif (event["expired"] - now).total_seconds() < 1800 and not event.get("half_hour"):
                    self.logger.info("Changing revolution task interval to 1 minute")
                    self.revolution.change_interval(minutes=1)
                    await self.send_excited_gif(guild_id, event, "HALF AN HOUR", "half_hour")

                elif (event["expired"] - now).total_seconds() < 900 and not event.get("quarter_hour"):
                    await self.send_excited_gif(guild_id, event, "15 MINUTES", "quarter_hour")

    async def send_excited_gif(self, guild_id: int, event: dict, hours_string: str, key: str):
        """
        Method for sending a countdown gif in regards to tickets and things
        :param guild_id:
        :param event:
        :param hours_string:
        :param key:
        :return:
        """
        guild_obj = await self.bot.fetch_guild(guild_id)  # type: discord.Guild
        channels = await guild_obj.fetch_channels()
        channel = [c for c in channels if c.id == event.get("channel_id", BSEDDIES_REVOLUTION_CHANNEL)][0]
        gif = await self.giphy_api.random_gif("celebrate")
        await channel.send(
            content=f"Just under **{hours_string.upper()}** to go now - remember to buy your tickets! 🎟️🎟️🎟️"
        )
        await channel.send(content=gif)
        self.revolutions.update({"_id": event["_id"]}, {"$set": {key: True}})

    async def create_event(self, guild_id: int, event: dict):
        """
        Handle event creation - this takes a DB entry and posts the message into the channel.

        We also set the Channel ID and the Message ID for the
        :param guild_id:
        :param event:
        :return:
        """
        king = self.user_points.get_current_king(guild_id)

        king_user = await self.bot.fetch_user(king["uid"])  # type: discord.User
        guild_obj = await self.bot.fetch_guild(guild_id)  # type: discord.Guild
        role = guild_obj.get_role(BSEDDIES_KING_ROLES[guild_id])  # type: discord.Role
        channels = await guild_obj.fetch_channels()
        channel = [c for c in channels if c.id == event.get("channel_id", BSEDDIES_REVOLUTION_CHANNEL)][0]

        message = self.embed_manager.get_revolution_message(king_user, role, event)
        message_obj = await channel.send(content=message)  # type: discord.Message
        self.revolutions.update(
            {"_id": event["_id"]}, {"$set": {"message_id": message_obj.id, "channel_id": message_obj.channel.id}}
        )

        await message_obj.add_reaction("🎟️")
        gif = await self.giphy_api.random_gif("revolution")
        await channel.send(content=gif)

    async def handle_resolving_bet(self, guild_id: int, event: dict):
        """
        Method for handling an event that needs resolving.

        We take the event chance and see if we generate a number between 0-100 that's lower than it. If it is, then
        we "win", otherwise we "lose". We handle both those conditions here too.
        :param guild_id:
        :param event:
        :return:
        """
        chance = event["chance"]
        king_id = event.get("king", self.user_points.get_current_king(guild_id)["uid"])
        ticket_buyers = event["ticket_buyers"]
        channel_id = event["channel_id"]

        guild_obj = await self.bot.fetch_guild(guild_id)
        channels = await guild_obj.fetch_channels()
        channel = [c for c in channels if c.id == channel_id][0]

        if len(ticket_buyers) == 0:
            message = f"No-one bought a ticket so there are no winners here."
            await channel.send(content=message)
            self.revolutions.close_event(event["event_id"], guild_id, False, 0)
            return

        king_user = await self.bot.fetch_user(king_id)

        val = (random.random() * 100)
        success = val <= chance

        self.logger.debug(f"Number was: {val} and chance was: {chance}")
        points_to_lose = 0

        if not success:
            # revolution FAILED
            eddies = event["eddies_spent"]
            message = (f"Sadly, our revolution has failed. THE KING LIVES :crown: {king_user.mention} will gain "
                       f"an additional `{eddies}` eddies. Better luck next week!")

            self.user_points.increment_points(king_id, guild_id, eddies)
            self.user_points.append_to_transaction_history(
                king_id, guild_id,
                {
                    "type": TransactionTypes.REV_TICKET_KING_WIN,
                    "amount": eddies,
                    "event_id": event["event_id"],
                    "timestamp": datetime.datetime.now(),
                    "comment": "User survived a REVOLUTION",
                }
            )
            gif = await self.giphy_api.random_gif("disappointed")

        else:
            king_dict = self.user_points.find_user(king_id, guild_id, projection={"points": True})
            points_to_lose = math.floor(event.get('locked_in_eddies', king_dict["points"]) / 2)

            points_each = math.floor(points_to_lose / len(ticket_buyers))

            message = (f"SUCCESS! THE KING IS DEAD! We have successfully taken eddies away from the KING. "
                       f"{king_user.mention} will lose **{points_to_lose}** and each ticker holder will gain "
                       f"`{points_each}`.")

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

            for user_id in ticket_buyers:
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

        await channel.send(content=message)
        await channel.send(content=gif)
        self.revolutions.close_event(event["event_id"], guild_id, success, points_to_lose)

    @revolution.before_loop
    async def before_revolution(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
