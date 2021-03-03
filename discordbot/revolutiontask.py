import datetime
import math
import random

import discord
from discord.ext import tasks, commands

from discordbot.constants import BSEDDIES_KING_ROLES
from discordbot.embedmanager import EmbedManager
from mongo.bsepoints import UserPoints
from mongo.bseticketedevents import RevolutionEvent


class BSEddiesRevolutionTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger):
        self.bot = bot
        self.user_points = UserPoints()
        self.revolutions = RevolutionEvent()
        self.embed_manager = EmbedManager(logger)
        self.logger = logger
        self.guilds = guilds
        self.revolution.start()

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.revolution.cancel()

    @tasks.loop(seconds=20)
    async def revolution(self):
        """
        Constantly checks to make sure that all events have been closed properly or raised correctly
        :return:
        """
        now = datetime.datetime.now()
        for guild_id in self.guilds:

            open_events = self.revolutions.get_open_events(guild_id)
            for event in open_events:

                message = event.get("message_id")
                if message is None:
                    await self.create_event(guild_id, event)
                    continue

                if now > event["expired"]:
                    await self.handle_resolving_bet(guild_id, event)
                    continue

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
        channel = [c for c in channels if c.id == 814087061619212299][0]

        message = self.embed_manager.get_revolution_message(king_user, role, event)
        message_obj = await channel.send(content=message)  # type: discord.Message
        self.revolutions.update(
            {"_id": event["_id"]}, {"$set": {"message_id": message_obj.id, "channel_id": message_obj.guild.id}}
        )

        await message_obj.add_reaction("🎟️")
        await channel.send(content="https://media.giphy.com/media/4NiFoaN9ufCOKbbn2i/giphy.gif")

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

        success = (random.random() * 100) < chance

        points_to_lose = 0
        if not success:
            # revolution FAILED
            eddies = event["eddies_spent"]
            message = (f"Sadly, our revolution has failed. THE KING LIVES :crown: {king_user.mention} will gain "
                       f"an additional `{eddies}` eddies. Better luck next week!")
            await channel.send(content=message)

        else:
            king_dict = self.user_points.find_user(king_id, guild_id, projection={"points": True})
            points_to_lose = math.floor(king_dict["points"] / 2)

            points_each = math.floor(points_to_lose / len(ticket_buyers))

            message = (f"SUCCESS! THE KING IS DEAD! We have successfully taken eddies away from the KING. "
                       f"{king_user.mention} will lose **{points_to_lose}** and each ticker holder will gain "
                       f"`{points_each}`.")
            await channel.send(content=message)
        self.revolutions.close_event(event["event_id"], guild_id, success, points_to_lose)

    @revolution.before_loop
    async def before_revolution(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
