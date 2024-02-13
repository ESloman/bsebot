"""Mocks for embeds."""

import datetime
import random

from bson import ObjectId

from mongo.datatypes.revolution import RevolutionEventDB


def get_event() -> RevolutionEventDB:
    """Returns a revolution dict for embed generating."""
    return RevolutionEventDB(
        _id=ObjectId(),
        guild_id=123456,
        channel_id=654321,
        message_id=246810,
        king=123,
        type="revolution",
        event_id="0001",
        created=datetime.datetime.now(),
        expired=datetime.datetime.now() + datetime.timedelta(minutes=5),
        open=True,
        chance=60,
        revolutionaries=[random.randint(500, 1000) for _ in range(3)],
        supporters=[random.randint(500, 1000) for _ in range(3)],
        locked_in_eddies=25400,
    )
