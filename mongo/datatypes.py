"""Database object types."""

import datetime
from dataclasses import dataclass, field
from typing import TypedDict

try:
    from typing import NotRequired, Optional
except ImportError:
    from typing import Optional

    NotRequired = Optional

from bson import ObjectId

from discordbot.bot_enums import ActivityTypes, SupporterType, TransactionTypes
from discordbot.constants import CREATOR
from mongo.basedatatypes import BaseDBObject, ImplementsMessage, NamedDBObject


@dataclass(frozen=True)
class Transaction(BaseDBObject):
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
class Activity(BaseDBObject):
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
class UserDB(NamedDBObject):
    """Represents a user in the database."""

    # basic user information
    uid: int
    """The discord user ID."""

    # eddies stuff
    points: int
    """The amount of eddies the user has in the server."""
    king: bool
    """Whether the user is KING in the server."""
    daily_eddies: bool = False
    """Whether the user receives daily eddie messages."""
    daily_summary: bool = False
    """Whether the user receives the daily eddies summary message."""
    pending_points: int = field(default=0)
    """The number of eddies the user has on pending bets."""
    high_score: int = field(default=0)
    """The user's highest ever amount of eddies."""
    daily_minimum: int | None = None
    """The minimum amount of eddies the user is going to get each day."""
    supporter_type: SupporterType = SupporterType.NEUTRAL
    """The user's alignment."""
    inactive: bool = False
    """Whether the user has left the server or not."""

    # DEPRECATED
    transaction_history: list[Transaction] | None = field(default_factory=list)
    """*DEPRECATED*"""
    activity_history: list[Activity] | None = field(default_factory=list)
    """*DEPCREATED*"""
    last_cull_time: datetime.datetime | None = None
    """*DEPRECATED*"""
    cull_warning: bool | None = None
    """*DEPRECATED*"""


@dataclass(frozen=True)
class BetterDB:
    """Represents a better on a bet."""

    user_id: int
    """The ID of the user."""
    emoji: str
    """The emoji the user bet with."""
    points: int
    """The amount of eddies the user put in on this bet."""
    first_bet: datetime.datetime | None = None
    """The time the user put in their first bet."""
    last_bet: datetime.datetime | None = None
    """The time the user put in their last bet."""


@dataclass(frozen=True)
class OptionDB:
    """A dict representing an option in a bet."""

    val: str
    """The human outcome name."""


@dataclass(frozen=True)
class BetDB(BaseDBObject, ImplementsMessage):
    """A dict representing a bet."""

    # general info
    bet_id: int
    """The bet ID of the bet"""
    user: int
    """The ID of the user who created the bet."""
    title: str
    """Title of the bet."""
    created: datetime.datetime
    """The time the bet was created."""
    timeout: datetime.datetime
    """When the bet will stop taking bets."""
    active: bool
    """Whether the bet is accepting new bets or not."""
    updated: datetime.datetime | None = None
    """When the bet was last updated."""

    # bet options
    options: list[str] = field(default=list)
    """List of option emojis."""
    option_vals: list[str] = field(default=list)
    """List of option values."""
    users: list[int] = field(default=list)
    """List of user IDs."""
    betters: dict[str, BetterDB] = field(default=dict)
    """A dict of user ID keys to their bet amounts."""
    result: str | None = None
    """The outcome of the bet."""
    option_dict: dict[str, OptionDB] = field(default=dict)
    """a dict of emoji keys to the human readable names."""
    private: bool = False
    """Whether the bet was made in a private channel."""
    closed: datetime.datetime | None = None
    """Date the bet was closed."""
    last_bet: datetime.datetime | None = None
    """When the last bet was."""


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


class Emoji(TypedDict):
    """A dict representing an emoji."""

    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the emoji is in"""
    eid: int
    """The discord emoji ID of the emoji"""
    name: str
    """Name of the emoji"""
    created_by: int
    """The discord user ID of the user who created the emoji"""
    created: datetime.datetime
    """When the emoji was created"""


class Sticker(TypedDict):
    """A dict representing a sticker."""

    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the sticker is in"""
    sid: int
    """The discord sticker ID of the sticker"""
    name: str
    """Name of the sticker"""
    created_by: int
    """The discord user ID of the user who created the sticker"""
    created: datetime.datetime
    """When the sticker was created"""


class RevolutionEventType(TypedDict):
    """A dict representing a revolution event."""

    _id: ObjectId
    """The internal DB ID"""
    type: str
    """Event type"""
    event_id: str
    """The event ID"""
    created: datetime.datetime
    """When the event was created"""
    expired: datetime.datetime
    """When the event will expire and 'resolve'"""
    chance: int
    """The chance of success"""
    ticket_cost: int
    """DEPRECATED"""
    ticket_buyers: list[int]
    """DEPRECATED"""
    supporters: list[int]
    """list of those supporting the event"""
    revolutionaries: list[int]
    """list of those revolutioning the event"""
    neutrals: list[int]
    """list of those impartial to the event"""
    locked: list[int]
    """Users who can't change their decision"""
    users: list[int]
    """everyone who's subscribed to the event"""
    open: bool
    """whether the event is still open"""
    message_id: int
    """The event's discord message ID"""
    channel_id: int
    """The discord channel ID where the event is happening"""
    guild_id: int
    """The discord server ID of the server the event is in"""
    king: int
    """The king the event affects"""
    points_distributed: int
    """The number of eddies given out if the event succeeds"""
    eddies_spent: int
    """DEPRECATED"""
    success: bool
    """Whether the event was a success or not"""
    locked_in_eddies: int
    """Number of eddies the King had when the event triggered"""
    times_saved: int
    """Number of times the king tried to save themselves"""
    one_hour: bool
    """Whether the one hour warning was triggered"""
    quarter_hour: bool
    """Whether the 15 minute warning was triggered"""


@dataclass(frozen=True)
class ThreadDB(NamedDBObject):
    """A dict representing a thread."""

    thread_id: int
    """The discord thread ID of the thread"""
    active: bool
    """Only for SPOILER threads - if we should still be posting spoiler warnings"""
    day: int | None = None
    """Only for SPOILER threads - the day a new ep comes out"""
    created: datetime.datetime | None = None
    """When the thread was created"""
    owner: int | None = field(default=CREATOR)
    """The discord user ID of the user who created the thread"""


@dataclass(frozen=True)
class GuildDB(NamedDBObject):
    """A dict representing a guild/server."""

    # general server info
    owner_id: int
    """The ID of the user that owns the server."""
    created: datetime.datetime | None = None
    """When the server was created."""
    admins: list[int] = field(default_factory=list)
    """List of BSEddies admins in the server."""

    # bseddies stuff
    daily_minimum: int | None = None
    """The daily minimum number of eddies."""
    category: int | None = None
    """The ID of the category the BSEddies channel is in."""
    channel: int | None = None
    """The ID of the BSEddies channel."""
    tax_rate: float = 0.1
    """The standard eddies tax rate."""
    supporter_tax_rate: float = 0
    """The eddies tax rate for supporters."""
    tax_rate_history: list[dict] = field(default_factory=list)
    """The tax rate history."""

    # KING stuff
    role: int | None = None
    """The role ID for the KING role."""
    king: int | None = None
    """The user ID of the user that is currently KING."""
    king_since: datetime.datetime | None = None
    """Start time of the current KING's rule."""
    king_history: list[dict] = field(default_factory=list)
    """The KING history."""
    rename_king: datetime.datetime | None = None
    """When the King was last renamed."""
    revolution: bool = False
    """Whether revolution is enabled."""
    supporter_role: int | None = None
    """The ID of the role for supporters."""
    revolutionary_role: int | None = None
    """The ID of the role for revolutionaries."""
    pledged: list[int] = field(default_factory=list)
    """The list of users pledged to support the KING this cycle."""

    # wordle stuff
    wordle: bool = False
    """Whether to post the wordle in this server."""
    wordle_channel: int | None = None
    """The channel ID of the channel to post the wordle in."""
    wordle_reminders: bool = False
    """Whether wordle reminders are enabled or not."""
    wordle_x_emoji: str | None = None
    """The emoji to use for X wordle scores."""
    wordle_two_emoji: str | None = None
    """The emoji to use for 2 wordle scores."""
    wordle_six_emoji: str | None = None
    """The emoji to use for 6 wordle scores."""

    # valorant stuff
    valorant_rollcall: bool = False
    """Whether to do valorant roll call messages."""
    valorant_channel: int | None = None
    """The channel ID of the 'valorant' channel."""
    valorant_role: int | None = None
    """The role ID of the 'valorant' role."""

    # message timers
    last_remind_me_suggest_time: datetime.datetime | None = None
    """The last time we triggered a 'remind me' message."""
    last_ad_time: datetime.datetime | None = None
    """The last time we triggered a 'marvel ad' message."""
    last_revolution_time: datetime.datetime | None = None
    """The last time we triggered a 'revolution' message."""
    last_rigged_time: datetime.datetime | None = None
    """The last time we triggered a 'rigged' message."""

    # update stuff
    hash: str | None = None  # noqa: A003
    """The last git hash."""
    release_ver: str | None = None
    """The last version of release notes published."""
    release_notes: bool = False
    """Whether to post release notes."""
    update_messages: bool = False
    """Whether to post bot update messages."""


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
