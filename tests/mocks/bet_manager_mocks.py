"""Bet Manager mocks."""


def get_bet_dict(idx: int) -> dict[str, any]:
    """Returns the bet dict at the specified index."""
    bets: list[dict[str, any]] = [
        {
            "_id": "1",
            "title": "some title",
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

    return bets[idx]
