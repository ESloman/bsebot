import datetime
import math

from discordbot.constants import BSE_SERVER_ID, BSEDDIES_REVOLUTION_CHANNEL

from mongo.bsepoints import UserPoints
from mongo.bseticketedevents import RevolutionEvent


if __name__ == "__main__":
    """
    Insert a revolution event in the DB
    """
    points = UserPoints()
    revs = RevolutionEvent()

    king_user = points.get_current_king(BSE_SERVER_ID)
    all_users = points.get_all_users_for_guild(BSE_SERVER_ID)

    user_points = king_user["points"]

    ticket_cost = math.ceil(((user_points / 2) / len(all_users)) + 5)

    revs.create_event(
        BSE_SERVER_ID,
        datetime.datetime.now(),
        datetime.datetime.now() + datetime.timedelta(hours=3),
        ticket_cost,
        king_user["uid"],
        BSEDDIES_REVOLUTION_CHANNEL
    )
