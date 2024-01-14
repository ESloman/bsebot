"""Our reminder datatypes."""

import datetime
from dataclasses import dataclass

from mongo.datatypes.basedatatypes import GuildedDBObject, ImplementsMessage


@dataclass(frozen=True)
class ReminderDB(GuildedDBObject, ImplementsMessage):
    """A dict representing a reminder."""

    created: datetime.datetime
    """When the reminder was created."""
    user_id: int
    """The ID of the user that created the reminder."""
    timeout: datetime.datetime
    """When the reminder times out."""
    active: bool
    """Whether the reminder is active."""
    reason: str
    """The reason for the reminder."""
    comment: str = ""
    """An additional comment."""
