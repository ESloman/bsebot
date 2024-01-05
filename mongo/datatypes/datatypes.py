"""Database object types."""

import datetime
from dataclasses import dataclass, field

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from mongo.datatypes.basedatatypes import BaseDBObject, ImplementsMessage, NamedDBObject


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
class ReactionDB:
    """A dict representing a user reaction."""

    user_id: int
    """The discord ID of the user who sent the reaction."""
    content: str
    """The reaction."""
    timestamp: datetime.datetime
    """When the reaction happened."""
    is_bot: bool = False
    """Whether the reply was from a bot."""


@dataclass(frozen=True)
class ReplyDB:
    """Represents a user reply."""

    user_id: int
    """The discord ID of the user who sent the reply."""
    content: str
    """The reply content."""
    timestamp: datetime.datetime
    """When the reply happened."""
    message_id: str
    """The discord ID of the message."""
    is_bot: bool = False
    """Whether the reply was from a bot."""


@dataclass(frozen=True)
class MessageDB(BaseDBObject, ImplementsMessage):
    """A dict representing a user message."""

    # message info
    user_id: int
    """The discord user ID of the user who sent the message."""
    timestamp: datetime.datetime
    """When the message was sent"""
    content: str = ""
    """Message content."""
    message_type: list[str] = field(default_factory=list)
    """The message classification"""
    is_thread: bool = False
    """Whether the message happened in a thread or not."""
    is_vc: bool = False
    """Whether the message represents a VC interaction or not."""
    is_bot: bool = False
    """Whether the message was sent by a bot."""

    # message reactions
    reactions: list[ReactionDB] | None = None
    """List of reactions."""
    replies: list[ReplyDB] | None = None
    """List of replies."""

    # edit stuff
    edit_count: int = 0
    """Number of edits made to this message."""
    edited_at: datetime.datetime | None = None
    """When this message was last edited."""
    content_old: list[str] = field(default_factory=list)
    """The list of previous message contents."""

    # emoji / sticker stuff
    emoji_id: int | None = None
    """The discord ID of the emoji for the 'emoji_created' interaction type."""
    sticker_id: int | None = None
    """The discord ID of the sticker for the 'sticker_created' interaction type."""
    created_at: datetime.datetime | None = None
    """The time the emoji / sticker was created."""
    edited: datetime.datetime | None = None
    """The time the emoji / sticker was edited."""
    og_mid: int | None = None
    """The discord ID of the message when the user users a sticker or emoji."""


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
