"""Mocks for tasks."""

import random

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
