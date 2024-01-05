"""Database object types."""

import datetime
from dataclasses import dataclass, field

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from mongo.datatypes.basedatatypes import BaseDBObject, ImplementsMessage, NamedDBObject
from mongo.datatypes.message import MessageDB


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
class VCInteractionDB(MessageDB):
    """A dict representing a voice channel interaction."""

    active: bool = False
    time_in_vc: float | None = None
    events: list[dict] = field(default_factory=list)
    left: datetime.datetime | None = None

    # muted
    muted: bool = False
    muted_time: datetime.datetime | None = None
    time_muted: float = 0

    # deafened
    deafened: bool = False
    deafened_time: datetime.datetime | None = None
    time_deafened: float = 0

    # streaming
    streaming: bool = False
    streaming_time: datetime.datetime | None = None
    time_streaming: float = 0


@dataclass(frozen=True)
class WordleMessageDB(MessageDB):
    """To represent a wordle message."""

    guesses: int = 0
    """The number of guesses for this wordle."""


@dataclass(frozen=True)
class EmojiDB(NamedDBObject):
    """A dict representing an emoji."""

    eid: int
    """The discord ID of the emoji."""
    created_by: int
    """The discord ID of the user who created the emoji."""
    created: datetime.datetime
    """When the emoji was created."""


@dataclass(frozen=True)
class StickerDB(NamedDBObject):
    """A dict representing a sticker."""

    stid: int
    """The discord ID of the sticker."""
    created_by: int
    """The discord ID of the user who created the sticker."""
    created: datetime.datetime
    """When the sticker was created."""


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
