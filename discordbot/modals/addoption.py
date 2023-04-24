
import datetime
from logging import Logger

import discord

import discordbot.views.bet  # avoiding a circular import (:
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.utilities import PlaceHolderLogger
from mongo.bsepoints.bets import UserBets
from mongo.datatypes import Bet


class AddBetOption(discord.ui.Modal):
    def __init__(
        self,
        bet: Bet,
        bseddies_place: PlaceBet,
        bseddies_close: CloseBet,
        logger: Logger = PlaceHolderLogger,
        *args,
        **kwargs
    ) -> None:
        super().__init__(*args, title="Add bet outcomes", **kwargs)

        # option emojis
        self.multiple_options_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "0️⃣"]

        self.logger: Logger = logger
        self.bet: Bet = bet
        self.place: PlaceBet = bseddies_place
        self.close: CloseBet = bseddies_close
        self.embed_manager = EmbedManager()
        self.user_bets = UserBets()

        self.bet_options = discord.ui.InputText(
            label="Enter the new outcome(s) on separate lines",
            placeholder="New outcome 1...\nNew outcome 2...\nNew outcome 3...\netc, etc...",
            style=discord.InputTextStyle.long
        )

        self.add_item(self.bet_options)

    async def callback(self, interaction: discord.Interaction):
        """

        :param interaction:
        :return:
        """
        await interaction.response.defer(ephemeral=True)

        outcome = self.bet_options.value
        outcomes = outcome.split("\n")

        now = datetime.datetime.now()

        if not outcomes:
            await interaction.followup.send(
                content="You need to provide at least one additional outcome",
                ephemeral=True,
                delete_after=10
            )
            return

        outcome_count = len(self.bet["options"])

        if len(outcomes) + outcome_count > 10:
            await interaction.followup.send(
                content="A bet cannot have more than ten outcomes",
                ephemeral=True,
                delete_after=10
            )
            return

        self.bet["options"].extend(outcomes)

        for outcome in outcomes:
            _index = outcome_count + outcomes.index(outcome)
            _emoji = self.multiple_options_emojis[_index]
            self.bet["option_dict"][_emoji] = {"val": outcome}

        # extend bet's timeout
        created = self.bet["created"]
        ending = self.bet["timeout"]

        expired = now - created
        ending += expired

        self.bet["timeout"] = ending

        self.user_bets.update(
            {"_id": self.bet["_id"]},
            {
                "$set": {
                    "options": self.bet["options"],
                    "option_dict": self.bet["option_dict"],
                    "updated": now,
                    "timeout": ending
                }
            }
        )

        channel = await interaction.guild.fetch_channel(self.bet["channel_id"])
        message = await channel.fetch_message(self.bet["message_id"])
        embed = self.embed_manager.get_bet_embed(interaction.guild, self.bet["bet_id"], self.bet)
        view = discordbot.views.bet.BetView(self.bet, self.place, self.close)
        await message.edit(embed=embed, view=view)
        await interaction.followup.send(content="Sorted.", ephemeral=True)
