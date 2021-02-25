import datetime
import math

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import BET_OUTCOME_COUNT_MODIFIER
from mongo.bsepoints import UserBets, UserPoints


class BetManager(object):
    def __init__(self, logger):
        self.logger = logger
        self.user_bets = UserBets()
        self.user_points = UserPoints()

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

        if modifier <= 1:
            modifier = 1.05
        elif modifier > 2:
            modifier = 2

        # assign winning points to the users who got the answer right
        for better in [b for b in ret["betters"] if ret["betters"][b]["emoji"] == emoji]:
            points_bet = ret["betters"][better]["points"]
            points_won = math.ceil(points_bet * modifier)
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

        return ret_dict
