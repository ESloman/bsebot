
import datetime
import math

import discord

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.constants import BSEDDIES_KING_ROLES
from discordbot.embedmanager import EmbedManager

from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.datatypes import RevolutionEventType
from mongo.bseticketedevents import RevolutionEvent


class RevolutionView(discord.ui.View):
    def __init__(self, client: discord.Client, event: RevolutionEventType, logger):
        super().__init__(timeout=None)
        self.client = client
        self.event_id = event["event_id"]
        self.locked_in = event["locked"]
        self.revolutions = RevolutionEvent()
        self.user_points = UserPoints()
        self.guilds = Guilds()
        self.embeds = EmbedManager(logger)
        self.activities = UserActivities()
        self.logger = logger

    def toggle_stuff(self, disable):
        for child in self.children:
            child.disabled = disable

    @discord.ui.button(
        label="OVERTHROW",
        style=discord.ButtonStyle.green,
        custom_id="overthrow_button",
        emoji="🔥"
    )
    async def overthrow_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        response = interaction.response  # type: discord.InteractionResponse
        followup = interaction.followup  # type: discord.Webhook

        self.toggle_stuff(True)

        # disable these whilst we do revolution stuff
        await response.edit_message(view=self)

        event = self.revolutions.get_event(interaction.guild.id, self.event_id)

        if not event["open"]:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        now = datetime.datetime.now()

        if event["expired"] < now:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        our_user = self.user_points.find_user(
            user_id,
            guild_id,
            {"points": True, "king": True}
        )

        if our_user.get("king", False):
            await followup.send(content="You ARE the King - you can't overthrow yourself.", ephemeral=True)
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in event["revolutionaries"]:
            await followup.send(
                content="You've already acted on this - you cannot do so again",
                ephemeral=True
            )
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in self.locked_in:
            await followup.send(
                content="You've pledged your support this week - you _cannot_ change your decision.",
                ephemeral=True
            )
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in event["supporters"]:
            event["chance"] += 15
            event["supporters"].remove(user_id)

        event["revolutionaries"].append(user_id)
        event["chance"] += 15

        if user_id not in event["users"]:
            event["users"].append(user_id)

        self.revolutions.update(
            {"_id": event["_id"]},
            {"$set": {
                "chance": event["chance"],
                "supporters": event["supporters"],
                "revolutionaries": event["revolutionaries"],
                "users": event["users"]
            }}
        )

        self.activities.add_activity(
            user_id,
            guild_id,
            ActivityTypes.REV_OVERTHROW,
            event_id=event["event_id"]
        )

        king_id = self.guilds.get_king(guild_id)

        king_user = await self.client.fetch_user(king_id)  # type: discord.User
        guild = self.client.get_guild(guild_id)

        role = guild.get_role(BSEDDIES_KING_ROLES[guild_id])

        edited_message = self.embeds.get_revolution_message(king_user, role, event, guild)

        self.toggle_stuff(False)

        await followup.edit_message(interaction.message.id, view=self, content=edited_message)
        await followup.send(content="Congrats - you've pledged to `overthrow`!", ephemeral=True)

    @discord.ui.button(
        label="SUPPORT THE KING",
        style=discord.ButtonStyle.red,
        custom_id="support_button",
        emoji="👑"
    )
    async def support_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        response = interaction.response  # type: discord.InteractionResponse
        followup = interaction.followup  # type: discord.Webhook

        self.toggle_stuff(True)

        # disable these whilst we do revolution stuff
        await response.edit_message(view=self)

        event = self.revolutions.get_event(interaction.guild.id, self.event_id)

        if not event["open"]:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        now = datetime.datetime.now()

        if event["expired"] < now:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        our_user = self.user_points.find_user(
            user_id,
            guild_id,
            {"points": True, "king": True}
        )

        if our_user.get("king", False):
            await followup.send(content="You ARE the King - you can't support yourself.", ephemeral=True)
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in event["supporters"]:
            await followup.send(
                content="You've already acted on this - you cannot do so again",
                ephemeral=True
            )
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in self.locked_in:
            await followup.send(
                content="You've pledged your support this week - you _cannot_ change your decision.",
                ephemeral=True
            )
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        if user_id in event["revolutionaries"]:
            event["chance"] -= 15
            event["revolutionaries"].remove(user_id)

        if user_id not in event["users"]:
            event["users"].append(user_id)

        if user_id not in event["supporters"]:
            event["supporters"].append(user_id)
            event["chance"] -= 15

        self.revolutions.update(
            {"_id": event["_id"]},
            {"$set": {
                "chance": event["chance"],
                "supporters": event["supporters"],
                "revolutionaries": event["revolutionaries"],
                "users": event["users"]
            }}
        )

        self.activities.add_activity(
            user_id,
            guild_id,
            ActivityTypes.REV_SUPPORT,
            event_id=event["event_id"]
        )

        king_id = self.guilds.get_king(guild_id)

        king_user = await self.client.fetch_user(king_id)  # type: discord.User
        guild = self.client.get_guild(guild_id)

        role = guild.get_role(BSEDDIES_KING_ROLES[guild_id])

        edited_message = self.embeds.get_revolution_message(king_user, role, event, guild)

        self.toggle_stuff(False)

        await followup.edit_message(interaction.message.id, view=self, content=edited_message)
        await followup.send(content="Congrats - you've pledged your `support`!", ephemeral=True)

    @discord.ui.button(
        label="Save THYSELF",
        style=discord.ButtonStyle.grey,
        custom_id="save_button",
        emoji="💵"
    )
    async def save_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        response = interaction.response  # type: discord.InteractionResponse
        followup = interaction.followup  # type: discord.Webhook

        self.toggle_stuff(True)

        # disable these whilst we do revolution stuff
        await response.edit_message(view=self)

        event = self.revolutions.get_event(interaction.guild.id, self.event_id)

        if not event["open"]:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        now = datetime.datetime.now()

        if event["expired"] < now:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True)
            # leave it disabled
            return

        if event["king"] != interaction.user.id:
            await followup.send(content="You're not the King - so you can't use this button.", ephemeral=True)
            self.toggle_stuff(False)
            await followup.edit_message(interaction.message.id, view=self)
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        our_user = self.user_points.find_user(
            user_id,
            guild_id,
            {"points": True, "king": True}
        )

        eddies = our_user["points"]
        amount_to_subtract = math.floor(eddies * 0.1)
        self.user_points.increment_points(
            user_id,
            guild_id,
            amount_to_subtract * -1,
            TransactionTypes.REVOLUTION_SAVE
        )

        self.activities.add_activity(
            user_id,
            guild_id,
            ActivityTypes.REV_SAVE,
            event_id=event["event_id"]
        )

        event["chance"] -= 15
        event["times_saved"] += 1
        self.revolutions.update(
            {"_id": event["_id"]},
            {"$set": {
                "chance": event["chance"],
                "times_saved": event["times_saved"]
            }}
        )

        guild = self.client.get_guild(guild_id)

        role = guild.get_role(BSEDDIES_KING_ROLES[guild_id])

        edited_message = self.embeds.get_revolution_message(interaction.user, role, event, guild)

        msg = f"{interaction.user.mention} just spent `{amount_to_subtract}` to reduce the overthrow chance by **15%**."
        await followup.send(content=msg)
        self.toggle_stuff(False)
        await followup.edit_message(interaction.message.id, view=self, content=edited_message)
