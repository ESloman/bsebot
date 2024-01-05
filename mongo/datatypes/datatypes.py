"""Database object types."""

import datetime
from dataclasses import dataclass

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from mongo.datatypes.basedatatypes import BaseDBObject, ImplementsMessage


@dataclass(frozen=True)
class TransactionDB(BaseDBObject):
    """A dict representing a transaction."""

    uid: int
    """The ID of the user the transaction relates to."""
    type: TransactionTypes  # noqa: A003
    """The type of transaction."""
    amount: int
    """The amount of eddies in the transaction."""
    timestamp: datetime.datetime
    """The time the transaction took place."""
    comment: str
    """The comment pertaining to a transaction."""
    bet_id: str | None = None
    """Bet ID of the transaction."""


@dataclass(frozen=True)
class ActivityDB(BaseDBObject):
    """A dict representing an activity."""

    uid: int
    """The ID of the user the transaction relates to."""
    type: ActivityTypes  # noqa: A003
    """The type of transaction."""
    timestamp: datetime.datetime
    """The time the activity took place."""
    comment: str
    """The comment pertaining to the activity."""


@dataclass(frozen=True)
class ReminderDB(BaseDBObject, ImplementsMessage):
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
