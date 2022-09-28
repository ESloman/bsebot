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

        point_one = (0, 2)
        point_two = (winning_outcome_eddies, modifier)
        try:
            m = ((point_two[1] - point_one[1]) / (point_two[0] - point_one[0]))
        except ZeroDivisionError:
            m = 0
            # this mean no-one won :(
        c = (point_two[1] - (m * point_two[0]))

        # get eddies the losers bet
        try:
            _extra_eddies = sum(ret_dict["losers"].values())
        except Exception as e:
            _extra_eddies = 0

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
