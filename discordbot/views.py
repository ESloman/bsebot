
import datetime
from typing import List

import discord

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BSEDDIES_KING_ROLES
from discordbot.embedmanager import EmbedManager
from discordbot.selects import BetSelect, BetOutcomesSelect, BetSelectAmount

from mongo.bsepoints import UserPoints
from mongo.bseticketedevents import RevolutionEvent


class LeaderBoardView(discord.ui.View):
    def __init__(self, embed_manager: EmbedManager):
        self.embeds = embed_manager
        super().__init__(timeout=None)

    @discord.ui.button(label="Expand", style=discord.ButtonStyle.primary)
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Button Callback
        :param button:
        :param interaction:
        :return:
        """
        msg = self.embeds.get_leaderboard_embed(
            interaction.guild,
            None if button.label == "Expand" else 5
        )

        button.label = "Expand" if button.label == "Retract" else "Retract"
        await interaction.response.edit_message(view=self, content=msg)


class HighScoreBoardView(discord.ui.View):
    def __init__(self, embed_manager: EmbedManager):
        self.embeds = embed_manager
        super().__init__()

    @discord.ui.button(label="Expand", style=discord.ButtonStyle.primary)
    async def button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        """
        Button Callback
        :param button:
        :param interaction:
        :return:
        """
        msg = self.embeds.get_highscore_embed(
            interaction.guild,
            None if button.label == "Expand" else 5
        )

        button.label = "Expand" if button.label == "Retract" else "Retract"
        await interaction.response.edit_message(view=self, content=msg)


class PlaceABetView(discord.ui.View):
    def __init__(self, bet_ids: list, user_eddies: int, submit_callback: callable):
        super().__init__(timeout=60)
        self.add_item(BetSelect(bet_ids))

        if len(bet_ids) == 1 and "option_dict" in bet_ids[0]:
            outcomes = bet_ids[0]["option_dict"]
            options = [
                discord.SelectOption(
                    label=outcomes[key]["val"],
                    value=key,
                    emoji=key
                ) for key in outcomes
            ]
        else:
            options = []

        self.add_item(BetOutcomesSelect(options))
        self.add_item(BetSelectAmount(user_eddies))

        self.submit_callback = submit_callback

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="This `place` command timed out - please _place_ another one", view=None)

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=3, disabled=True, custom_id="submit_btn")
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        data = {}
        for child in self.children:
            if child.custom_id == "bet_select":
                try:
                    data["bet_id"] = child.values[0]
                except IndexError:
                    # this means that this was default
                    data["bet_id"] = child.options[0].value
            elif child.custom_id == "outcome_select":
                data["emoji"] = child.values[0]
            elif child.custom_id == "amount_select":
                data["amount"] = int(child.values[0])

        # call the callback that actually places the bet
        await self.submit_callback(
            interaction,
            data["bet_id"],
            data["amount"],
            data["emoji"]
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=3, disabled=False, custom_id="cancel_btn")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)


class CloseABetView(discord.ui.View):
    def __init__(self, bet_ids: list, submit_callback: callable):
        super().__init__(timeout=60)
        self.add_item(BetSelect(bet_ids))

        if len(bet_ids) == 1 and "option_dict" in bet_ids[0]:
            outcomes = bet_ids[0]["option_dict"]
            options = [
                discord.SelectOption(
                    label=outcomes[key]["val"],
                    value=key,
                    emoji=key
                ) for key in outcomes
            ]
        else:
            options = []

        self.add_item(BetOutcomesSelect(options, "submit_btn"))
        self.submit_callback = submit_callback

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True, custom_id="submit_btn")
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        data = {}
        for child in self.children:
            if child.custom_id == "bet_select":
                try:
                    data["bet_id"] = child.values[0]
                except IndexError:
                    # this means that this was default
                    data["bet_id"] = child.options[0].value
            elif child.custom_id == "outcome_select":
                data["emoji"] = child.values[0]

        # call the callback that actually places the bet
        await self.submit_callback(
            interaction,
            data["bet_id"],
            data["emoji"]
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, row=2, disabled=False, custom_id="cancel_btn")
    async def cancel_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Cancelled", view=None)


class BetView(discord.ui.View):
    def __init__(self, bet, bseddies_place, bseddies_close):
        super().__init__()
        self.bet = bet
        self.place = bseddies_place
        self.close = bseddies_close

    @discord.ui.button(label="Place a bet", style=discord.ButtonStyle.blurple)
    async def place_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.place.create_bet_view(interaction, [self.bet, ])

    @discord.ui.button(label="Close this bet", style=discord.ButtonStyle.gray)
    async def close_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await self.close.create_bet_view(interaction, [self.bet, ])


class RevolutionView(discord.ui.View):
    def __init__(self, client: discord.Client, event: dict, logger):
        super().__init__(timeout=None)
        self.client = client
        self.event_id = event["event_id"]
        self.revolutions = RevolutionEvent()
        self.user_points = UserPoints()
        self.embeds = EmbedManager(logger)
        self.logger = logger

    def toggle_stuff(self, disable):
        for child in self.children:
            child.disabled = disable

    @discord.ui.button(label=f"OVERTHROW", style=discord.ButtonStyle.green)
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

        event["chance"] += 15

        if user_id not in event["revolutionaries"]:
            event["revolutionaries"].append(user_id)
        if user_id not in event["users"]:
            event["users"].append(user_id)

        event["supporters"].pop(user_id)

        self.revolutions.update(
            {"_id": event["_id"]}, event
        )

        self.user_points.append_to_transaction_history(
            user_id, guild_id,
            {
                "type": TransactionTypes.REV_OVERTHROW,
                "event_id": event["event_id"],
                "timestamp": datetime.datetime.now(),
            }
        )

        king = self.user_points.get_current_king(guild_id)

        king_user = await self.client.fetch_user(king["uid"])  # type: discord.User
        guild = self.client.get_guild(guild_id)

        role = guild.get_role(BSEDDIES_KING_ROLES[guild_id])

        edited_message = self.embeds.get_revolution_message(king_user, role, event)

        self.toggle_stuff(False)

        await followup.edit_message(interaction.message.id, view=self, content=edited_message)
        await followup.send(content="Congrats - you've pledged your `support`!", ephemeral=True)

    @discord.ui.button(label=f"SUPPORT THE KING", style=discord.ButtonStyle.red)
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

        event["chance"] -= 15

        if user_id not in event["supporters"]:
            event["supporters"].append(user_id)
        if user_id not in event["users"]:
            event["users"].append(user_id)

        event["revolutionaries"].pop(user_id)

        self.revolutions.update(
            {"_id": event["_id"]}, event
        )

        self.user_points.append_to_transaction_history(
            user_id, guild_id,
            {
                "type": TransactionTypes.REV_SUPPORT,
                "event_id": event["event_id"],
                "timestamp": datetime.datetime.now(),
            }
        )

        king = self.user_points.get_current_king(guild_id)

        king_user = await self.client.fetch_user(king["uid"])  # type: discord.User
        guild = self.client.get_guild(guild_id)

        role = guild.get_role(BSEDDIES_KING_ROLES[guild_id])

        edited_message = self.embeds.get_revolution_message(king_user, role, event)

        self.toggle_stuff(False)

        await followup.edit_message(interaction.message.id, view=self, content=edited_message)
        await followup.send(content="Congrats - you've pledged your `support`!", ephemeral=True)
