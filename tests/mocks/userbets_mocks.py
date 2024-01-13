"""UserBets mocks."""

import datetime

from bson import ObjectId

from mongo.bsepoints.bets import UserBets
from mongo.datatypes.bet import BetDB, BetterDB
from tests.mocks import interface_mocks


def user_bets_count_data() -> list[tuple[BetDB, int]]:
    """Returns some data for testing bet point counting."""
    return [
        (
            BetDB(
                123,
                456,
                ObjectId(),
                654,
                "0001",
                321,
                "some bet",
                datetime.datetime.now(),
                True,
                betters={"123": BetterDB(123, "", 5), "456": BetterDB(123, "", 10)},
            ),
            15,
        ),
        (BetDB(123, 456, ObjectId(), 654, "0001", 321, "some bet", datetime.datetime.now(), True, betters={}), 0),
        (
            BetDB(
                123,
                456,
                ObjectId(),
                654,
                "0001",
                321,
                "another bet",
                datetime.datetime.now(),
                True,
                betters={"123": BetterDB(123, "", 100)},
            ),
            100,
        ),
    ]


def user_pending_points_query(query: dict) -> list[dict]:
    """Mocks our pending points query.

    Returns any bets that match the user so we can mock the counting bit.
    """
    response = interface_mocks.query_mock("userbets", {"guild_id": query["guild_id"]})
    _user_id = next(iter(query.keys())).split(".")[-1]
    return [
        UserBets.make_data_class(bet)
        for bet in response
        if str(_user_id) in bet.get("betters", {}) and "betters" in bet
    ]
