"""Mocks for embeds."""

import datetime
import random


def get_bet() -> dict:
    """Returns a bet dict for embed generating."""
    return {
        "option_dict": {"1": {"val": "one"}, "2": {"val": "two"}},
        "betters": {
            "123456": {"user_id": 123456, "emoji": "1", "points": 10},
            "654321": {"user_id": 654321, "emoji": "2", "points": 20},
        },
        "active": True,
        "timeout": datetime.datetime.now(),
    }


def get_event() -> dict:
    """Returns a revolution dict for embed generating."""
    return {
        "chance": 60,
        "revolutionaries": [random.randint(500, 1000) for _ in range(3)],
        "supporters": [random.randint(500, 1000) for _ in range(3)],
        "locked_in_eddies": 25400,
    }
