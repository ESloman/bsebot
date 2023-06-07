import datetime
from dataclasses import dataclass
from typing import Optional, Union

from discordbot.bot_enums import AwardsTypes, StatTypes


@dataclass
class Stat:
    type: str
    guild_id: int
    short_name: str
    timestamp: datetime.datetime
    value: Union[int, float, datetime.datetime]
    annual: bool
    month: Optional[str] = None
    year: Optional[str] = None
    user_id: Optional[int] = None
    award: Optional[AwardsTypes] = None
    stat: Optional[StatTypes] = None
    eddies: Optional[int] = None
    kwargs: Optional[dict] = None


@dataclass
class StatsData:
    total_messages: int
    average_length: float
    average_words: float
    total_swears: int
    top_channels: tuple[int, int]
    top_swears: tuple[int, int]
    top_users: tuple[int, int]
    replies_count: int
    replied_count: int
