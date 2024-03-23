"""Contains our BetManager for resolving bets.

Gives out winner eddies and also updates the DB accordingly.
"""

import contextlib
import datetime
import math
import random

from slomanlogger import SlomanLogger

from discordbot.bot_enums import SupporterType, TransactionTypes
from discordbot.constants import BET_OUTCOME_COUNT_MODIFIER, SMALL_BET_AMOUNT
from mongo.bsepoints.bets import UserBets
from mongo.bsepoints.guilds import Guilds
from mongo.bsepoints.points import UserPoints


class BetManager:
    """BetManager class for bet resolving.

    Args:
        logger (Logger): logger for logging
        user_bets (UserBets): user_bets collection class
        user_points (UserPoints): user_points collection class
        guilds (Guilds): guilds collection class
    """

    def __init__(self: "BetManager") -> None:
        """Initialisation method.

        Args:
            logger (Logger): the logging object to use
        """
        self.logger = SlomanLogger("bsebot")
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.guilds = Guilds()

    @staticmethod
    def calculate_bet_modifiers(
        total_eddies_bet: int,
        winning_outcome_eddies: int,
        options_count: int,
        losers_count: int,
    ) -> tuple[float, float]:
        """Calculates the bet winnings multiplier and coefficient.

        Args:
            total_eddies_bet (int): the total eddies bet
            winning_outcome_eddies (int): the total eddies bet on the winning outcome
            options_count (int): the number of options in the bet
            losers_count (int): _description_

        Returns:
            tuple[float, float]: the multiplier and coeffient
        """
        try:
            modifier = (2 - (winning_outcome_eddies / total_eddies_bet)) + BET_OUTCOME_COUNT_MODIFIER[options_count]
        except ZeroDivisionError:
            modifier = 1

        modifier += random.random() / 2

        if modifier <= 1:
            modifier = 1.05

        if losers_count == 0:
            # no losers and only winnners
            modifier = 1.2

        point_one = (0, 2 + (random.random() / 2))
        point_two = (winning_outcome_eddies, modifier)
        try:
            multiplier = (point_two[1] - point_one[1]) / (point_two[0] - point_one[0])
        except ZeroDivisionError:
            multiplier = 0
            # this mean no-one won :(
        coefficient = point_two[1] - (multiplier * point_two[0])

        return multiplier, coefficient

    @staticmethod
    def _calculate_single_bet_winnings(
        points_bet: int, multiplier: float, coefficient: float, extra_eddies: int, num_winners: int
    ) -> int:
        """Calculate single bet winnings.

        Returns the points won based on the inputs.

        Args:
            self (BetManager): _description_
            points_bet (int): _description_
            multiplier (float): _description_
            coefficient (float): _description_
            extra_eddies (int): _description_
            num_winners (int): _description_

        Returns:
            int: the points won
        """
        points_won = math.ceil(((multiplier * points_bet) + coefficient) * points_bet)

        if points_bet < SMALL_BET_AMOUNT:
            points_won += points_bet

        # add on loser points
        with contextlib.suppress(ValueError, ZeroDivisionError, TypeError):
            points_won += int(math.floor(extra_eddies / num_winners))
        return points_won

    def _calculate_taxed_winnings(
        self,
        better_id: int,
        guild_id: int,
        tax: tuple[int, int],
        actual_amount_won: int,
        points_won: int,
    ) -> tuple[int, int]:
        """Calculates the taxed winnings.

        Args:
            better_id (int): the better ID
            guild_id (int): the guild ID
            tax (tuple): the normal tax rate and supporter tax rate
            actual_amount_won (int): the amount of eddies actually won
            points_won (int):

        Returns:
            tuple[int, int]: eddiws_won, tax
        """
        tax_value, supporter_tax = tax
        user_db = self.user_points.find_user(int(better_id), guild_id)
        tr = supporter_tax if user_db.supporter_type == SupporterType.SUPPORTER else tax_value
        tax_amount = math.floor(actual_amount_won * tr)
        eddies_won_minus_tax = points_won - tax_amount
        return eddies_won_minus_tax, tax_amount

    def _process_bet_winner(
        self: "BetManager",
        bet_id: str,
        guild_id: int,
        better_id: str,
        eddies_won_minus_tax: int,
    ) -> None:
        """Processes a bet winner.

        Adds the eddies to the winner's total.

        Args:
            bet_id (str): the bet ID
            guild_id (int): the guild ID
            better_id (str): the winner ID
            eddies_won_minus_tax (int): the eddies the user actually will get
        """
        self.logger.debug("%s won - incrementing eddies by %s", better_id, eddies_won_minus_tax)
        self.user_points.increment_points(
            int(better_id),
            guild_id,
            eddies_won_minus_tax,
            TransactionTypes.BET_WIN,
            bet_id=bet_id,
        )

    def close_a_bet(self: "BetManager", bet_id: str, guild_id: int, emoji: list[str]) -> dict[str, any]:
        """Close a bet from a given bet ID.

        Here we also calculate who the winners are and allocate their winnings to them.

        Args:
            bet_id (str): the Id of the bet to close
            guild_id (int): the guild ID the bet resides in
            emoji (list[str]): the winning result of the bet

        Returns:
            dict: a result_dict that has some info about the winners and losers
        """
        bet = self.user_bets.get_bet_from_id(guild_id, bet_id)

        self.user_bets.close_a_bet(bet._id, emoji)  # noqa: SLF001

        ret_dict = {
            "result": emoji,
            "outcome_name": [bet.option_dict[e] for e in emoji],
            "timestamp": datetime.datetime.now(tz=datetime.UTC),
            "losers": {b: bet.betters[b].points for b in bet.betters if bet.betters[b].emoji not in emoji},
            "winners": {},
        }

        total_eddies_bet = sum([bet.betters[b].points for b in bet.betters])
        winning_outcome_eddies = sum(
            [bet.betters[b].points for b in bet.betters if bet.betters[b].emoji in emoji],
        )

        multiplier, coefficient = self.calculate_bet_modifiers(
            total_eddies_bet,
            winning_outcome_eddies,
            len(bet.options),
            len(ret_dict["losers"]),
        )

        self.logger.info("Bet %s winnings has multiplier %s and coefficient %s", bet_id, multiplier, coefficient)

        # get eddies the losers bet
        try:
            _extra_eddies = sum(ret_dict["losers"].values())
        except (KeyError, TypeError, ValueError, AttributeError):
            _extra_eddies = 0

        # get tax value
        tax_value, supporter_tax = self.guilds.get_tax_rate(guild_id)

        # total eddies won and total taxes
        total_eddies_winnings = 0
        total_eddies_won = 0
        total_eddies_taxed = 0

        # assign winning points to the users who got the answer right
        winners = [b for b in bet.betters if bet.betters[b].emoji in emoji]
        for better_id in winners:
            points_bet = bet.betters[better_id].points
            points_won = self._calculate_single_bet_winnings(
                points_bet, multiplier, coefficient, _extra_eddies, len(winners)
            )
            actual_amount_won = points_won - points_bet
            eddies_won_minus_tax, tax_amount = self._calculate_taxed_winnings(
                better_id, guild_id, (tax_value, supporter_tax), actual_amount_won, points_won
            )

            self._process_bet_winner(bet_id, guild_id, better_id, eddies_won_minus_tax)

            self.logger.debug(
                "%s bet %s eddies and won %s (%s) - getting taxed %s so %s",
                better_id,
                points_bet,
                actual_amount_won,
                points_won,
                tax_amount,
                eddies_won_minus_tax,
            )

            total_eddies_won += points_won
            total_eddies_winnings += actual_amount_won
            total_eddies_taxed += tax_amount
            ret_dict["winners"][better_id] = eddies_won_minus_tax

        self.logger.debug(
            "Bet ID: %s, eddies won: %s, eddies won (with original bets): %s, eddies taxed: %s",
            bet_id,
            total_eddies_winnings,
            total_eddies_won,
            total_eddies_taxed,
        )

        # give taxed eddies to the King
        king_id = self.guilds.get_king(guild_id)
        self.user_points.increment_points(
            king_id,
            guild_id,
            total_eddies_taxed,
            TransactionTypes.BET_TAX,
            bet_id=bet_id,
        )

        ret_dict["king_tax"] = total_eddies_taxed
        ret_dict["king"] = king_id
        ret_dict["total_winnings"] = total_eddies_winnings

        # add winnings to the bet entry in the database for future purposes
        self.user_bets.update({"bet_id": bet_id, "guild_id": guild_id}, {"$set": {"winners": ret_dict["winners"]}})

        return ret_dict
