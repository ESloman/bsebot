"""Mocks for embeds."""

import datetime


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
