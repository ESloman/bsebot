"""Revolution views."""

import datetime
import math
from zoneinfo import ZoneInfo

import discord

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.views.bseview import BSEView
from mongo.bsepoints.activities import UserActivities
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints
from mongo.bseticketedevents import RevolutionEvent
from mongo.datatypes.revolution import RevolutionEventDB


class RevolutionView(BSEView):
    """Class for revolution view."""

    _SAVE_THYSELF_BUTTON_TEXT = "Save THYSELF"

    def __init__(self, client: BSEBot, event: RevolutionEventDB) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the BSEBot client
            event (RevolutionEventType): the revolution event
        """
        super().__init__(timeout=None)
        self.client = client
        self.event_id = event.event_id
        self.locked_in = event.locked
        self.revolutions = RevolutionEvent()
        self.user_points = UserPoints()
        self.guilds = Guilds()
        self.embeds = EmbedManager()
        self.activities = UserActivities()

    def toggle_stuff(self, disable: bool) -> None:
        """Toggle children.

        Args:
            disable (bool): whether the children are disabled or not
        """
        if disable:
            self.disable_all_items()
        else:
            self.enable_all_items()

    async def _handle_save_thyself_button_checks(
        self, interaction: discord.Interaction, button: discord.Button, user_id: int, king_id: int
    ) -> bool:
        if (user_id == king_id) and button.label != self._SAVE_THYSELF_BUTTON_TEXT:
            await interaction.followup.send(
                content="You ARE the King - you can't overthrow/support yourself.",
                ephemeral=True,
                delete_after=10,
            )
            self.toggle_stuff(False)
            await interaction.followup.edit_message(interaction.message.id, view=self)
            return False

        # check that users aren't using buttons they shouldn't
        if button.label == self._SAVE_THYSELF_BUTTON_TEXT and (user_id != king_id):
            await interaction.followup.send(
                content="You're not the King - so you can't use this button.",
                ephemeral=True,
                delete_after=10,
            )
            self.toggle_stuff(False)
            await interaction.followup.edit_message(interaction.message.id, view=self)
            return False
        return True

    async def _handle_non_save_thyself_buttons(
        self, interaction: discord.Interaction, user_id: int, event: RevolutionEventDB, faction_event_key: str
    ) -> bool:
        if user_id not in event.users:
            event.users.append(user_id)

        # make sure user isn't doing the same thing twice
        if user_id in getattr(event, faction_event_key, []):
            await interaction.followup.send(
                content="You've already acted on this - you cannot do so again",
                ephemeral=True,
                delete_after=10,
            )
            self.toggle_stuff(False)
            await interaction.followup.edit_message(interaction.message.id, view=self)
            return False

        # make sure locked in users stay locked in
        if user_id in self.locked_in:
            await interaction.followup.send(
                content="You've pledged your support this week - you _cannot_ change your decision.",
                ephemeral=True,
                delete_after=10,
            )
            self.toggle_stuff(False)
            await interaction.followup.edit_message(interaction.message.id, view=self)
            return False
        return True

    @staticmethod
    def _handle_overthrow_support_buttons(
        event: RevolutionEventDB,
        user_id: int,
        faction_event_key: str,
        other_faction_event_key: str,
        faction_chance: float,
    ) -> None:
        # reverse actions of other faction
        if user_id in getattr(event, other_faction_event_key):
            event.chance -= faction_chance * -1
            getattr(event, other_faction_event_key).remove(user_id)

        # apply our actions (increasing/reducing chance)
        getattr(event, faction_event_key).append(user_id)
        event.chance += faction_chance

        # remove user from neutrals if they're in it
        if user_id in event.neutrals:
            event.neutrals.remove(user_id)

    @staticmethod
    def _handle_impartial_button(
        event: RevolutionEventDB,
        user_id: int,
    ) -> None:
        if user_id in event.revolutionaries:
            event.chance -= 15
            event.revolutionaries.remove(user_id)
        elif user_id in event.supporters:
            event.chance += 15
            event.supporters.remove(user_id)

        if user_id not in event.neutrals:
            event.neutrals.append(user_id)

    def _handle_save_thyself_button(
        self, event: RevolutionEventDB, user_id: int, interaction: discord.Interaction
    ) -> str:
        # work out how many eddies to subtract
        our_user = self.user_points.find_user(user_id, interaction.guild_id, {"points": True, "king": True})
        eddies = our_user.points
        amount_to_subtract = math.floor(eddies * 0.1)
        self.user_points.increment_points(
            user_id,
            interaction.guild_id,
            amount_to_subtract * -1,
            TransactionTypes.REVOLUTION_SAVE,
        )

        event.chance -= 15
        event.times_saved += 1
        return f"<@{user_id}> just spent `{amount_to_subtract}` to reduce the overthrow chance by **15%**."

    async def _revolution_button_logic(  # noqa: PLR0915
        self, interaction: discord.Interaction, button: discord.Button
    ) -> None:
        """Function for abstracting the revolution button logic.

        The logic is slightly different for each of the buttons but there's a lot of
        shared functionality so we can reduce this complexity by putting it all in
        one place.

        Check that the revolution event is still valid; aka still open and not expired.
        Check that the right user isn't pressing the wrong buttons;
        - the king can't press support/overthrow
        - the king can only press SAVE THYSELF

        Defines some args based on the button pressed for use throughout the logic.

        Non king button:
            - check that we haven't already done the action we're pressing
            - check that we're not locked in to supporting

        If we're support/overthrow:
            - if we previously pressed the other button, reverse those effects
            - apply effects of this button
        If we're impartial:
            - remove from revolutionaries/supporters
            - increase/decrease chance accordingly
        If button is KING button:
            - calculate eddies to remove from King
            - remove those eddies
            - lower the chance

        Update event in DB
        Update message in discord
        Add transactions/activities to DB
        Send ephemeral message to user

        Args:
            interaction (discord.Interaction): _description_
            button (discord.Button): _description_
        """
        response = interaction.response
        followup = interaction.followup

        self.toggle_stuff(True)

        # disable these whilst we do revolution stuff
        await response.edit_message(view=self)

        event = self.revolutions.get_event(interaction.guild.id, self.event_id)

        # check event is still valid
        if not event.open:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True, delete_after=10)
            # leave it disabled
            return

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if event.expired < now:
            await followup.send(content="Unfortunately, this event has expired", ephemeral=True, delete_after=10)
            # leave it disabled
            return

        user_id = interaction.user.id
        guild_id = interaction.guild.id

        guild_db = self.guilds.get_guild(guild_id)
        king_id = guild_db.king

        if not await self._handle_save_thyself_button_checks(interaction, button, user_id, king_id):
            return

        # match statement for the variables that are different for the different factions
        match button.label:
            case "OVERTHROW":
                faction_event_key = "revolutionaries"
                other_faction_event_key = "supporters"
                faction_chance = 15
                act_type = ActivityTypes.REV_OVERTHROW
                msg = "Congrats - you've pledged to `overthrow`!"
            case "SUPPORT THE KING":
                faction_event_key = "supporters"
                other_faction_event_key = "revolutionaries"
                faction_chance = -15
                act_type = ActivityTypes.REV_SUPPORT
                msg = "Congrats - you've pledged your `support`!"
            case self._SAVE_THYSELF_BUTTON_TEXT:
                act_type = ActivityTypes.REV_SAVE
                msg = "Congrats - you've reduced the overthrow chance."
            case "Impartial":
                faction_event_key = "neutrals"
                act_type = ActivityTypes.REV_NEUTRAL
                msg = "Congrats - you're now impartial."

        event = event.unfrozen()

        if button.label != self._SAVE_THYSELF_BUTTON_TEXT:  # noqa: SIM102
            # only do this for the non-KING buttons
            if not await self._handle_non_save_thyself_buttons(interaction, user_id, event, faction_event_key):
                return

        if button.label in {"OVERTHROW", "SUPPORT THE KING"}:
            # logic for overthrow/supporting
            # different to king button logic
            self._handle_overthrow_support_buttons(
                event, user_id, faction_event_key, other_faction_event_key, faction_chance
            )

        elif button.label == "Impartial":
            # logic for user pressing the impartial button
            self._handle_impartial_button(event, user_id)

        elif button.label == self._SAVE_THYSELF_BUTTON_TEXT:
            # logic for saving thyself
            # it is different to supporter/revolutionary logic
            msg = self._handle_save_thyself_button(event, user_id, interaction)
            await interaction.channel.send(content=msg)

        # update DB with all the changes we've made
        self.revolutions.update(
            {"_id": event._id},  # noqa: SLF001
            {
                "$set": {
                    "chance": event.chance,
                    "supporters": event.supporters,
                    "revolutionaries": event.revolutionaries,
                    "neutrals": event.neutrals,
                    "users": event.users,
                    "times_saved": event.times_saved,
                },
            },
        )

        self.activities.add_activity(user_id, guild_id, act_type, event_id=event.event_id)

        # build new message and update it with updated event
        king_user = await self.client.fetch_user(king_id)  # type: discord.User
        guild = await self.client.fetch_guild(guild_id)
        role = guild.get_role(guild_db.role)
        edited_message = self.embeds.get_revolution_message(king_user, role, event, guild)
        self.toggle_stuff(False)

        await followup.edit_message(interaction.message.id, view=self, content=edited_message)

        if button.label != self._SAVE_THYSELF_BUTTON_TEXT:
            # only send followup for users
            await followup.send(content=msg, ephemeral=True, delete_after=10)

    @discord.ui.button(label="OVERTHROW", style=discord.ButtonStyle.green, custom_id="overthrow_button", emoji="🔥")
    async def overthrow_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for the Overthrow button.

        Defers to the button logic method for handling the logic.

        Args:
            button (discord.ui.Button): the button being pressed
            interaction (discord.Interaction): the interaction context
        """
        await self._revolution_button_logic(interaction, button)

    @discord.ui.button(label="SUPPORT THE KING", style=discord.ButtonStyle.red, custom_id="support_button", emoji="👑")
    async def support_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for the SUPPORT button.

        Defers to the button logic method for handling the logic.

        Args:
            button (discord.ui.Button): the button being pressed
            interaction (discord.Interaction): the interaction context
        """
        await self._revolution_button_logic(interaction, button)

    @discord.ui.button(label="Impartial", style=discord.ButtonStyle.blurple, custom_id="impartial_button", emoji="😐")
    async def impartial_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for the impartial button.

        Defers to the button logic method for handling the logic.

        Args:
            button (discord.ui.Button): _description_
            interaction (discord.Interaction): _description_
        """
        await self._revolution_button_logic(interaction, button)

    @discord.ui.button(label="Save THYSELF", style=discord.ButtonStyle.grey, custom_id="save_button", emoji="💵")
    async def save_callback(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        """Callback for the Save THYSELF button.

        Defers to the button logic method for handling the logic.

        Args:
            button (discord.ui.Button): the button being pressed
            interaction (discord.Interaction): the interaction context
        """
        await self._revolution_button_logic(interaction, button)
