
from typing import List

import discord

import discordbot.constants as constants
from discordbot.embedmanager import EmbedManager
from discordbot.selects import BetSelect, BetOutcomesSelect, BetSelectAmount


class LeaderBoardView(discord.ui.View):
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
        outcomes_select = BetOutcomesSelect([])
        self.add_item(BetSelect(bet_ids))
        self.add_item(outcomes_select)
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
                data["bet_id"] = child.values[0]
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
        self.add_item(BetOutcomesSelect([], "submit_btn"))
        self.submit_callback = submit_callback

    @discord.ui.button(label="Submit", style=discord.ButtonStyle.green, row=2, disabled=True, custom_id="submit_btn")
    async def submit_callback(self, button: discord.ui.Button, interaction: discord.Interaction):

        data = {}
        for child in self.children:
            if child.custom_id == "bet_select":
                data["bet_id"] = child.values[0]
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
