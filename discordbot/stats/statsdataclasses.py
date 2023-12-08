"""Stats data classes."""

import datetime
from dataclasses import dataclass

from discordbot.bot_enums import AwardsTypes, StatTypes


@dataclass
class Stat:
    """A stat representation."""

    type: str  # noqa: A003
    guild_id: int
    short_name: str
    timestamp: datetime.datetime
    value: int | (float | datetime.datetime)
    annual: bool
    month: str | None = None
    year: str | None = None
    user_id: int | list[int] | None = None
    award: AwardsTypes | None = None
    stat: StatTypes | None = None
    eddies: int | None = None
    kwargs: dict | None = None


@dataclass
class StatsData:
    """A stats data representation."""

    total_messages: int
    average_length: float
    average_words: float
    total_swears: int
    top_channels: tuple[int, int]
    top_swears: tuple[int, int]
    top_users: tuple[int, int]
    replies_count: int
    replied_count: int
    wordles: int
    average_wordle_score: float
