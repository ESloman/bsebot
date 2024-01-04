"""Database object types."""

import datetime
from dataclasses import dataclass, field
from typing import TypedDict

try:
    from typing import Optional, NotRequired
except ImportError:
    from typing import Optional

    NotRequired = Optional

from bson import ObjectId

from discordbot.bot_enums import ActivityTypes, TransactionTypes, SupporterType
from discordbot.constants import CREATOR

class Transaction(TypedDict):
    """A dict representing a transaction."""

    uid: int
    guild_id: int
    type: TransactionTypes
    """The type of transaction enum"""
    amount: int
    """The amount of eddies the transaction is concerned with"""
    timestamp: datetime.datetime
    """The time the transaction took place"""
    comment: str
    """Comment"""
    bet_id: NotRequired[str]
    """Bet ID of the transaction - if relevant"""


class Activity(TypedDict):
    """A dict representing an activity."""

    uid: int
    guild_id: int
    type: ActivityTypes
    """The activity type enum"""
    timestamp: datetime.datetime
    """The time the activity took place"""
    comment: str
    """Comment"""


@dataclass
class User:
    """A User dict."""

    _id: ObjectId
    """The internal DB ID"""
    uid: int
    """The discord user ID"""
    guild_id: int
    """The discord server ID the user belongs to"""
    name: str
    """The nickname for the guild or the user name"""
    points: int
    """The amount of eddies the user has in the server"""
    king: bool
    """Whether the user is KING in the server"""

    # optionals / defaults
    daily_eddies: bool = False
    """Whether the user receives daily eddie messages"""
    daily_summary: bool = False
    """Whether the user receives the daily eddies summary message"""
    pending_points: int = field(default=0)
    """The number of eddies the user has on pending bets"""
    high_score: int = field(default=0)
    """The user's highest ever amount of eddies"""
    daily_minimum: Optional[int] = None
    """The minimum amount of eddies the user is going to get each day"""
    supporter_type: SupporterType = SupporterType.NEUTRAL
    transaction_history: Optional[list[Transaction]] = field(default_factory=list)
    """A list of the transactions the user has made"""
    activity_history: Optional[list[Activity]] = field(default_factory=list)
    """A list of activities the user has made"""
    inactive: bool = False
    """Whether the user has left the server or not"""

    # DEPRECATED
    last_cull_time: Optional[datetime.datetime] = None
    """*DEPRECATED*"""
    cull_warning: Optional[bool] = None
    """*DEPRECATED*"""


class Better(TypedDict):
    """A dict representing a better on a bet."""

    user_id: int
    emoji: str
    first_bet: datetime.datetime
    last_bet: datetime.datetime
    points: int


class Option(TypedDict):
    """A dict representing an option in a bet."""

    val: str
    """The human outcome name"""


class Bet(TypedDict):
    """A dict representing a bet."""

    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the bet is in"""
    bet_id: int
    """The bet ID of the bet"""
    user: int
    """The discord User ID of the user who created the bet"""
    title: str
    """Title of the bet"""
    options: list[str]
    """List of option emojis"""
    option_vals: list[str]
    """List of option values"""
    users: list[int]
    """List of user IDs"""
    created: datetime.datetime
    """The time the bet was created"""
    timeout: datetime.datetime
    """When the bet will stop taking bets"""
    active: bool
    """Whether the bet is accepting new bets or not"""
    betters: dict[str:Better]
    """A dict of user ID keys to their bet amounts"""
    result: str | None
    """The outcome of the bet"""
    option_dict: dict[str, Option]
    """a dict of emoji keys to the human readable names"""
    channel_id: int
    """The channel the bet exists in"""
    message_id: int
    """The message ID of the bet"""
    private: bool
    """Whether the bet was made in a private channel"""
    closed: datetime.datetime
    """date the bet was closed"""


class Reaction(TypedDict):
    """A dict representing a user reaction."""

    user_id: int
    """The discord user ID of the user who sent the message"""
    content: str
    """The reaction"""
    timestamp: datetime.datetime
    """When the reaction happened"""


class Reply(TypedDict):
    """A dict representing a user reply."""

    user_id: int
    """The discord user ID of the user who sent the reply"""
    content: str
    """The reply"""
    timestamp: datetime.datetime
    """When the reply happened"""
    message_id: str
    """The reply message ID"""


class Message(TypedDict):
    """A dict representing a user message."""

    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the message is in"""
    message_id: int
    """The discord message ID of the message"""
    user_id: int
    """The discord user ID of the user who sent the message"""
    channel_id: int
    """The discord channel ID of the channel the message is in"""
    message_type: list[str]
    """The message classification"""
    content: str
    """Message content (fi anything)"""
    timestamp: datetime.datetime
    """When the message was sent"""
    reactions: NotRequired[list[Reaction]]
    """List of reactions"""
    replies: NotRequired[list[Reply]]
    """List of replies"""
    is_thread: NotRequired[bool]
    """Whether the message happened in a thread or not"""
    content_old: list[str]
    """The list of previous message contents"""
    edit_count: int
    """Number of edits made to this message"""
    edited_at: datetime.datetime
    """When this message was last edited"""


class VCInteraction(Message):
    """A dict representing a voice channel interaction."""

    muted: bool
    muted_time: datetime.datetime
    deafened: bool
    deafened_time: datetime.datetime
    streaming: bool
    streaming_time: datetime.datetime
    time_in_vc: float
    time_muted: float
    time_deafened: float
    time_streaming: float
    active: bool
    events: list[dict]
    left: datetime.datetime


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


@dataclass
class Thread:
    """A dict representing a thread."""

    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the thread is in"""
    thread_id: int
    """The discord thread ID of the thread"""
    name: str
    """Name of the thread"""
    day: int
    """Only for SPOILER threads - the day a new ep comes out"""
    active: bool
    """Only for SPOILER threads - if we should still be posting spoiler warnings"""
    created: Optional[datetime.datetime] = None
    """When the thread was created"""
    owner: Optional[int] = field(default=CREATOR)
    """The discord user ID of the user who created the thread"""


@dataclass
class GuildDB:
    """A dict representing a guild/server."""

    _id: ObjectId
    guild_id: int
    created: datetime.datetime
    owner_id: int
    channel: int
    wordle_reminders: bool
    category: int
    role: int
    daily_minimum: int
    name: str
    tax_rate: float
    supporter_tax_rate: float

    # optional vars
    admins: list[int] = field(default_factory=list)
    wordle: Optional[bool] = None
    wordle_channel: Optional[int] = None
    rename_king: Optional[datetime.datetime] = None
    tax_rate_history: list[dict] = field(default_factory=list)
    king: Optional[int] = None
    king_since: Optional[datetime.datetime] = None
    king_history: list[dict] = field(default_factory=list)
    hash: Optional[str] = None
    update_messages: Optional[bool] = None
    revolution: Optional[bool] = None
    supporter_role: Optional[int] = None
    revolutionary_role: Optional[int] = None
    pledged: list[int] = field(default_factory=list)
    release_ver: Optional[str] = None
    release_notes: Optional[bool] = None
    valorant_rollcall: Optional[bool] = None
    valorant_channel: Optional[int] = None
    valorant_role: Optional[int] = None
    wordle_x_emoji: Optional[str] = None
    wordle_two_emoji: Optional[str] = None
    wordle_six_emoji: Optional[str] = None
    last_remind_me_suggest_time: Optional[datetime.datetime] = None
    last_ad_time: Optional[datetime.datetime] = None
    last_revolution_time: Optional[datetime.datetime] = None
    last_rigged_time: Optional[datetime.datetime] = None


@dataclass
class Reminder:
    """A dict representing a reminder."""

    _id: ObjectId
    guild_id: int
    created: datetime.datetime
    user_id: int
    timeout: datetime.datetime
    active: bool
    reason: str
    channel_id: int
    message_id: int
