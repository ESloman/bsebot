
"""
The BetManager is for resolving bets
Gives out winner eddies and also updates the DB accordingly
"""

import datetime
import math
import random

from discordbot.bot_enums import TransactionTypes, SupporterType
from discordbot.constants import BET_OUTCOME_COUNT_MODIFIER
from mongo.bsepoints import Guilds, UserBets, UserPoints


class BetManager(object):
    def __init__(self, logger):
        self.logger = logger
        self.user_bets = UserBets()
        self.user_points = UserPoints()
        self.guilds = Guilds()

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
        except Exception:
            _extra_eddies = 0

        # get tax value
        tax_value, supporter_tax = self.guilds.get_tax_rate(guild_id)

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

            user_db = self.user_points.find_user(int(better), guild_id)
            tr = supporter_tax if user_db.get("supporter_type", 0) == SupporterType.SUPPORTER else tax_value

            total_eddies_won += points_won
            actual_amount_won = points_won - points_bet  # the actual winnings without original bet
            total_eddies_winnings += actual_amount_won
            tax_amount = math.floor((actual_amount_won * tr))
            total_eddies_taxed += tax_amount
            eddies_won_minux_tax = points_won - tax_amount

            self.logger.info(
                f"{better} bet {points_bet} eddies and won {actual_amount_won} ({points_won}) - "
                f"getting taxed {tax_amount} so {eddies_won_minux_tax=}"
            )

            ret_dict["winners"][better] = eddies_won_minux_tax
            self.logger.info(f"{better} won - incrementing eddies by {eddies_won_minux_tax}")
            self.user_points.increment_points(int(better), guild_id, eddies_won_minux_tax)
            # add to transaction history
            update_result = self.user_points.append_to_transaction_history(
                int(better),
                guild_id,
                {
                    "type": TransactionTypes.BET_WIN,
                    "amount": eddies_won_minux_tax,
                    "timestamp": datetime.datetime.now(),
                    "bet_id": bet_id,
                }
            )
            self.logger.debug(f"Update result: {update_result.matched_count}, {update_result.modified_count}")
            if not update_result.modified_count:
                self.logger.debug("Update result was 0 - trying again without casting user to int")
                update_result = self.user_points.append_to_transaction_history(
                    better,
                    guild_id,
                    {
                        "type": TransactionTypes.BET_WIN,
                        "amount": eddies_won_minux_tax,
                        "timestamp": datetime.datetime.now(),
                        "bet_id": bet_id,
                    }
                )
                self.logger.debug(f"Second {update_result}")

        # give taxed eddies to the King
        self.logger.info(
            f"Bet ID: {bet_id}\n"
            f"Eddies won: {total_eddies_winnings}\n"
            f"Eddies won (with original bets): {total_eddies_won}\n"
            f"Eddies taxed: {total_eddies_taxed}\n"
        )

        king_id = self.guilds.get_king(guild_id)
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
