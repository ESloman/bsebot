"""Mocks for embeds."""

import datetime
import random
from dataclasses import asdict

from bson import ObjectId

from mongo.bsepoints import bets
from mongo.datatypes import BetDB, RevolutionEventType


def get_bet() -> BetDB:
    """Returns a bet dict for embed generating."""
    return bets.UserBets.make_data_class(
        asdict(
            BetDB(
                _id=ObjectId(),
                title="Some title",
                option_dict={"1": {"val": "one"}, "2": {"val": "two"}},
                betters={
                    "123456": {"user_id": 123456, "emoji": "1", "points": 10},
                    "654321": {"user_id": 654321, "emoji": "2", "points": 20},
                },
                bet_id=0,
                channel_id=123,
                message_id=456,
                user=123456,
                guild_id=654321,
                created=datetime.datetime.now(),
                timeout=datetime.datetime.now() + datetime.timedelta(minutes=5),
                active=True,
            )
        )
    )


def get_event() -> RevolutionEventType:
    """Returns a revolution dict for embed generating."""
    return RevolutionEventType(
        chance=60,
        revolutionaries=[random.randint(500, 1000) for _ in range(3)],
        supporters=[random.randint(500, 1000) for _ in range(3)],
        locked_in_eddies=25400,
    )
