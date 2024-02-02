"""Our thread datatype."""

import dataclasses
import datetime

from discordbot.constants import CREATOR
from mongo.datatypes.basedatatypes import NamedDBObject


@dataclasses.dataclass(frozen=True)
class ThreadDB(NamedDBObject):
    """A dict representing a thread."""

    thread_id: int
    """The discord thread ID of the thread."""
    active: bool
    """Only for SPOILER threads - if we should still be posting spoiler warnings."""
    day: int | None = None
    """Only for SPOILER threads - the day a new ep comes out."""
    created: datetime.datetime | None = None
    """When the thread was created."""
    owner: int | None = dataclasses.field(default=CREATOR)
    """The discord ID of the user who created the thread."""

    # deprecated
    creator: int | None = None
    """DEPRECATED - The discord ID of the user who created the thread."""
