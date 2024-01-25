"""Our bot activity datatypes."""

import dataclasses
import datetime

from mongo.datatypes.basedatatypes import BaseDBObject


@dataclasses.dataclass(frozen=True)
class BotActivityDB(BaseDBObject):
    """The bot activity DB."""

    category: str
    """The 'category' of activity. One of: listening, playing, watching."""
    name: str
    """The bot activity name."""
    created_by: int
    """The ID of the discord user that created this."""
    created: datetime.datetime
    """The date this activity was created."""
    count: int
    """How many times this one has been selected."""
    archived: bool
    """Whether the activity is archived or not."""
