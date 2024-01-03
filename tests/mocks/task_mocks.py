"""Mocks for tasks."""

import random
from collections import Counter

from discordbot.constants import HUMAN_MESSAGE_TYPES


def mock_eddie_manager_give_out_eddies(_: int, real: bool) -> dict:
    """Mocks the give out eddies function."""
    data = {}
    for _x in range(5):  # noqa: B007
        uid = random.randint(123456, 654321)
        message_types = random.choices(list(HUMAN_MESSAGE_TYPES.keys()), k=5)
        mock_breakdown = {_type: random.randint(0, 10) for _type in message_types}
        eddies = sum(mock_breakdown.values())
        tax = random.randint(0, 10)
        data[uid] = [eddies, mock_breakdown, tax]
    data[123500] = [0, {}, 0]
    return data


def mock_bseddies_manager_counters() -> list[tuple[Counter, int, float]]:
    """Returns various message counters to test the _calc_eddies function."""
    return [
        # the counter, the start value, the expected result
        (Counter(), 4, 4),
        (Counter(), 2, 2),
        (Counter({"message": 5}), 4, 4.75),
        (Counter({"message": 50}), 4, 11.5),
        (Counter({"message": 10, "reply": 1}), 4, 6),
        (Counter({"message": 10, "role_mention": 1}), 4, 6.5),
        (Counter({"message": 10, "reply": 5, "role_mention": 1}), 4, 9),
        (Counter({"message": 10, "mention": 5, "role_mention": 1}), 4, 11.5),
        (
            Counter({
                "message": 10,
                "mention": 5,
                "role_mention": 1,
                "emoji_used": 5,
                "reply": 10,
                "link": 2,
            }),
            4,
            28.9,
        ),
        (
            Counter({
                "message": 10,
                "mention": 5,
                "role_mention": 1,
                "emoji_used": 5,
                "reply": 10,
                "link": 2,
                "something_random": 10,
            }),
            4,
            28.9,
        ),
    ]
