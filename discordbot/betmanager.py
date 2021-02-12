from mongo.bsepoints import UserPoints, UserBets


class BetManager(object):
    def __init__(self):
        self.user_bets = UserBets()
        self.user_points = UserPoints()
