"""UserBets mocks."""

import datetime

from bson import ObjectId

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
    """Mocks our pending points query."""
    response = interface_mocks.query_mock("userbets", {"guild_id": query["guild_id"], "result": None})
    _user_id = next(iter(query.keys())).split(".")[-1]
    return [bet for bet in response if _user_id in bet.get("betters", {})]
