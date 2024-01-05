"""Bet Manager mocks."""

import datetime

from mongo.bsepoints.bets import UserBets
from mongo.datatypes import BetDB


def get_bet_dict(idx: int) -> BetDB:
    """Returns the bet dict at the specified index."""
    bets: list[BetDB] = [
        {
            "_id": "1",
            "title": "some title",
            "bet_id": "0",
            "channel_id": 123,
            "message_id": 456,
            "user": 123456,
            "guild_id": 654321,
            "created": datetime.datetime.now(),
            "timeout": datetime.datetime.now() + datetime.timedelta(minutes=5),
            "active": True,
            "option_dict": {":one:": {"val": "one"}, ":two:": {"val": "two"}},
            "betters": {
                "123": {"user_id": 123, "emoji": ":one:", "points": 100},
                "456": {"user_id": 456, "emoji": ":two:", "points": 100},
                "789": {"user_id": 789, "emoji": ":one:", "points": 100},
                "987": {"user_id": 987, "emoji": ":two:", "points": 100},
            },
            "options": [":one:", ":two:"],
        },
        {
            "_id": "2",
            "title": "some title",
            "bet_id": "1",
            "channel_id": 123,
            "message_id": 456,
            "user": 123456,
            "guild_id": 654321,
            "created": datetime.datetime.now(),
            "timeout": datetime.datetime.now() + datetime.timedelta(minutes=5),
            "active": True,
            "option_dict": {":one:": {"val": "one"}, ":two:": {"val": "two"}},
            "betters": {
                "123": {"user_id": 123, "emoji": ":one:", "points": 100},
                "456": {"user_id": 456, "emoji": ":one:", "points": 100},
                "789": {"user_id": 789, "emoji": ":one:", "points": 100},
                "987": {"user_id": 987, "emoji": ":one:", "points": 100},
            },
            "options": [":one:", ":two:"],
        },
    ]

    return UserBets.make_data_class(bets[idx])
