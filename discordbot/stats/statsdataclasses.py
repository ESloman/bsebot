import datetime
from dataclasses import dataclass
from typing import Optional, TypedDict, Union

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


### User Stats for `/stats` or `BSE Wrapped`


class UserMessageChannelStat(TypedDict):
    user_id: int
    number: int
    total_channels: int
    favourite_channel: int
    fc_messages: int
    least_favourite_channel: int
    lfc_messages: int
    thread_number: int
    total_threads: int
    favourite_thread: int
    ft_messages: int
    least_favourite_thread: int
    lft_messages: int
