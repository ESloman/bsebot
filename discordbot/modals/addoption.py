"""AddBetOption modal class."""

import copy
import datetime
from dataclasses import asdict
from logging import Logger

import discord
import pytz

import discordbot.views.bet
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.utilities import PlaceHolderLogger
from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB


class AddBetOption(discord.ui.Modal):
    """Add Bet Option modal class."""

    def __init__(
        self,
        bet: BetDB,
        bseddies_place: PlaceBet,
        bseddies_close: CloseBet,
        logger: Logger = PlaceHolderLogger,
        *args: tuple[any],
        **kwargs: dict[any],
    ) -> None:
        """Intialisation method.

        Args:
            bet (Bet): the bet
            bseddies_place (PlaceBet): the place class
            bseddies_close (CloseBet): the close class
            logger (Logger, optional): the loggger. Defaults to PlaceHolderLogger.
        """
        super().__init__(*args, title="Add bet outcomes", **kwargs)

        # option emojis
        self.multiple_options_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "0️⃣"]

        self.logger: Logger = logger
        self.bet: BetDB = bet
        self.place: PlaceBet = bseddies_place
        self.close: CloseBet = bseddies_close
        self.embed_manager = EmbedManager()
        self.user_bets = UserBets()

        self.bet_options = discord.ui.InputText(
            label="Enter the new outcome(s) on separate lines",
            placeholder="New outcome 1...\nNew outcome 2...\nNew outcome 3...\netc, etc...",
            style=discord.InputTextStyle.long,
        )

        self.add_item(self.bet_options)

    async def callback(self, interaction: discord.Interaction) -> None:
        """The submit callback.

        Args:
            interaction (discord.Interaction): the interaction
        """
        await interaction.response.defer(ephemeral=True)

        outcome = self.bet_options.value
        outcomes = outcome.split("\n")

        now = datetime.datetime.now(tz=pytz.utc)

        if not outcomes:
            await interaction.followup.send(
                content="You need to provide at least one additional outcome",
                ephemeral=True,
                delete_after=10,
            )
            return

        outcome_count = len(self.bet.options)

        if len(outcomes) + outcome_count > 10:  # noqa: PLR2004
            await interaction.followup.send(
                content="A bet cannot have more than ten outcomes",
                ephemeral=True,
                delete_after=10,
            )
            return

        new_options = self.bet.options + outcomes
        new_option_dict = {key: asdict(value) for key, value in self.bet.option_dict.items()}
        new_option_vals = copy.deepcopy(self.bet.option_vals)

        for outcome in outcomes:
            _index = outcome_count + outcomes.index(outcome)
            _emoji = self.multiple_options_emojis[_index]
            new_option_dict[_emoji] = {"val": outcome}
            new_option_vals.append(outcome)

        # extend bet's timeout
        created = self.bet.created
        ending = self.bet.timeout

        expired = now - created
        ending += expired

        self.bet.timeout = ending

        self.user_bets.update(
            {"_id": self.bet._id},  # noqa: SLF001
            {
                "$set": {
                    "options": new_options,
                    "option_dict": new_option_dict,
                    "updated": now,
                    "timeout": ending,
                    "option_vals": new_option_vals,
                },
            },
        )

        channel = await interaction.guild.fetch_channel(self.bet.channel_id)
        message = await channel.fetch_message(self.bet.message_id)
        embed = self.embed_manager.get_bet_embed(interaction.guild, self.bet)
        view = discordbot.views.bet.BetView(self.bet, self.place, self.close)
        await message.edit(embed=embed, view=view)
        await interaction.followup.send(content="Sorted.", ephemeral=True)
