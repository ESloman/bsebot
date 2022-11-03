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
