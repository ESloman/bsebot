import datetime
import math
import random

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BET_OUTCOME_COUNT_MODIFIER
from mongo.bsepoints import UserBets, UserPoints
from mongo.bsedataclasses import TaxRate


class BetManager(object):
    def __init__(self, logger):
        self.logger = logger
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.tax_rate = TaxRate()

    def close_a_bet(self, bet_id: str, guild_id: int, emoji: str) -> dict:
        """
        Close a bet from a bet ID.
        Here we also calculate who the winners are and allocate their winnings to them.

        :param bet_id: str - the bet to close
        :param guild_id: int - the guild ID the bet resides in
        :param emoji: str - the winning result of the bet
        :return: a result_dict that has some info about the winners and losers
        """

        ret = self.user_bets.get_bet_from_id(guild_id, bet_id)

        self.user_bets.close_a_bet(ret["_id"], emoji)

        ret_dict = {
            "result": emoji,
            "outcome_name": ret["option_dict"][emoji],
            "timestamp": datetime.datetime.now(),
            "losers": {b: ret["betters"][b]["points"]
                       for b in ret["betters"] if ret["betters"][b]["emoji"] != emoji},
            "winners": {}
        }

        total_eddies_bet = sum([ret["betters"][b]["points"] for b in ret["betters"]])
        winning_outcome_eddies = sum(
            [ret["betters"][b]["points"] for b in ret["betters"] if ret["betters"][b]["emoji"] == emoji]
        )

        try:
            modifier = (2 - (winning_outcome_eddies / total_eddies_bet)) \
                       + BET_OUTCOME_COUNT_MODIFIER[len(ret["options"])]
        except ZeroDivisionError:
            modifier = 1

        modifier += (random.random() / 2)
        
        if modifier <= 1:
            modifier = 1.05

        if len(ret_dict["losers"]) == 0:
            # no losers and only winnners
            modifier = 1.2
        
        point_one = (0, 2 + (random.random() / 2))
        point_two = (winning_outcome_eddies, modifier)
        try:
            m = ((point_two[1] - point_one[1]) / (point_two[0] - point_one[0]))
        except ZeroDivisionError:
            m = 0
            # this mean no-one won :(
        c = (point_two[1] - (m * point_two[0]))
        
        self.logger.info(f"Bet {bet_id} winnings has modifier {m} and coefficient {c}")

        # get eddies the losers bet
        try:
            _extra_eddies = sum(ret_dict["losers"].values())
        except Exception as e:
            _extra_eddies = 0

        # get tax value
        tax_value = self.tax_rate.get_tax_rate()
        
        # total eddies won and total taxes
        total_eddies_winnings = 0
        total_eddies_won = 0
        total_eddies_taxed = 0
        
        # assign winning points to the users who got the answer right
        winners = [b for b in ret["betters"] if ret["betters"][b]["emoji"] == emoji]
        for better in winners:
            points_bet = ret["betters"][better]["points"]
            points_won = math.ceil(((m * points_bet) + c) * points_bet)

            if points_bet < 10:
                points_won += points_bet

            # add on loser points
            try:
                points_won += int(math.floor(_extra_eddies / len(winners)))
            except Exception:
                pass
           
            total_eddies_won += points_won
            actual_amount_won = points_won - points_bet  # the actual winnings without original bet
            total_eddies_winnings += actual_amount_won
            tax_amount = actual_amount_won - math.floor((actual_amount_won * tax_value))
            total_eddies_taxed += tax_amount

            ret_dict["winners"][better] = points_won
            self.user_points.increment_points(int(better), guild_id, points_won)
            # add to transaction history
            self.user_points.append_to_transaction_history(
                int(better),
                guild_id,
                {
                    "type": TransactionTypes.BET_WIN,
                    "amount": points_won,
                    "timestamp": datetime.datetime.now(),
                    "bet_id": bet_id,
                }
            )

        # give taxed eddies to the King
        self.logger.info(
            f"Bet ID: {bet_id}\n"
            f"Eddies won: {total_eddies_winnings}\n"
            f"Eddies won (with original bets): {total_eddies_won}\n"
            f"Eddies taxed: {total_eddies_taxed}"
        )
        
        king_id = self.user_points.get_current_king(guild_id)["uid"]
        self.user_points.increment_points(king_id, guild_id, total_eddies_taxed)
        self.user_points.append_to_transaction_history(
            king_id,
            guild_id,
            {
                "type": TransactionTypes.BET_TAX,
                "amount": total_eddies_taxed,
                "timestamp": datetime.datetime.now(),
                "bet_id": bet_id,
            }
        )
        
        ret_dict["king_tax"] = total_eddies_taxed
        ret_dict["king"] = king_id
        ret_dict["total_winnings"] = total_eddies_winnings
        
        return ret_dict
