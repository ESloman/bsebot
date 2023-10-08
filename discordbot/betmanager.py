"""Contains our BetManager for resolving bets.

Gives out winner eddies and also updates the DB accordingly.
"""

import contextlib
import datetime
import math
import random
from logging import Logger

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


    def __init__(self: "BetManager", logger: Logger) -> None:
        """Initialisation method.

        Args:
            logger (Logger): the logging object to use
        """
        self.logger = logger
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

    def close_a_bet(self: "BetManager", bet_id: str, guild_id: int, emoji: list[str]) -> dict:
        """Close a bet from a given bet ID.

        Here we also calculate who the winners are and allocate their winnings to them.

        Args:
            bet_id (str): the Id of the bet to close
            guild_id (int): the guild ID the bet resides in
            emoji (list[str]): the winning result of the bet

        Returns:
            dict: a result_dict that has some info about the winners and losers
        """
        ret = self.user_bets.get_bet_from_id(guild_id, bet_id)

        self.user_bets.close_a_bet(ret["_id"], emoji)

        ret_dict = {
            "result": emoji,
            "outcome_name": [ret["option_dict"][e] for e in emoji],
            "timestamp": datetime.datetime.now(tz=datetime.UTC),
            "losers": {
                b: ret["betters"][b]["points"] for b in ret["betters"] if ret["betters"][b]["emoji"] not in emoji
            },
            "winners": {},
        }

        total_eddies_bet = sum([ret["betters"][b]["points"] for b in ret["betters"]])
        winning_outcome_eddies = sum(
            [ret["betters"][b]["points"] for b in ret["betters"] if ret["betters"][b]["emoji"] in emoji],
        )

        multiplier, coefficient = self.calculate_bet_modifiers(
            total_eddies_bet, winning_outcome_eddies, len(ret["options"]), len(ret_dict["losers"]),
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
        winners = [b for b in ret["betters"] if ret["betters"][b]["emoji"] in emoji]
        for better in winners:
            points_bet = ret["betters"][better]["points"]
            points_won = math.ceil(((multiplier * points_bet) + coefficient) * points_bet)

            if points_bet < SMALL_BET_AMOUNT:
                points_won += points_bet

            # add on loser points
            with contextlib.suppress(ValueError, ZeroDivisionError, TypeError):
                points_won += int(math.floor(_extra_eddies / len(winners)))

            user_db = self.user_points.find_user(int(better), guild_id)
            tr = supporter_tax if user_db.get("supporter_type", 0) == SupporterType.SUPPORTER else tax_value

            total_eddies_won += points_won
            actual_amount_won = points_won - points_bet  # the actual winnings without original bet
            total_eddies_winnings += actual_amount_won
            tax_amount = math.floor(actual_amount_won * tr)
            total_eddies_taxed += tax_amount
            eddies_won_minux_tax = points_won - tax_amount

            self.logger.info(
                "%s bet %s eddies and won %s (%s) - getting taxed %s so %s",
                better, points_bet, actual_amount_won, points_won, tax_amount, eddies_won_minux_tax,
            )

            ret_dict["winners"][better] = eddies_won_minux_tax
            self.logger.info("%s won - incrementing eddies by %s", better, eddies_won_minux_tax)
            self.user_points.increment_points(
                int(better), guild_id, eddies_won_minux_tax, TransactionTypes.BET_WIN, bet_id=bet_id,
            )

        # give taxed eddies to the King
        self.logger.info(
            "Bet ID: %s, eddies won: %s, eddies won (with original bets): %s, eddies taxed: %s",
            bet_id, total_eddies_winnings, total_eddies_won, total_eddies_taxed,
        )

        king_id = self.guilds.get_king(guild_id)
        self.user_points.increment_points(
            king_id, guild_id, total_eddies_taxed, TransactionTypes.BET_TAX, bet_id=bet_id,
        )

        ret_dict["king_tax"] = total_eddies_taxed
        ret_dict["king"] = king_id
        ret_dict["total_winnings"] = total_eddies_winnings

        # add winnings to the bet entry in the database for future purposes
        self.user_bets.update({"bet_id": bet_id, "guild_id": guild_id}, {"$set": {"winners": ret_dict["winners"]}})

        return ret_dict
