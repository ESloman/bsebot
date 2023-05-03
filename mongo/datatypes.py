
import datetime
from typing import TypedDict, Union

try:
    from typing import NotRequired
except ImportError:
    from typing import Optional
    NotRequired = Optional

from bson import ObjectId

from discordbot.bot_enums import ActivityTypes, TransactionTypes, SupporterType


class Transaction(TypedDict):
    """
    A dict representing a transaction
    """
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
    uid: int
    guild_id: int
    type: ActivityTypes
    """The activity type enum"""
    timestamp: datetime.datetime
    """The time the activity took place"""
    comment: str
    """Comment"""


class User(TypedDict):
    """A User dict
    """
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
    pending_points: int
    """The number of eddies the user has on pending bets"""
    inactive: bool
    """Whether the user has left the server or not"""
    transaction_history: list[Transaction]
    """A list of the transactions the user has made"""
    activity_history: list[Activity]
    """A list of activities the user has made"""
    daily_eddies: bool
    """Whether the user receives daily eddie messages"""
    daily_summary: bool
    """Whether the user receives the daily eddies summary message"""
    king: bool
    """Whether the user is KING in the server"""
    last_cull_time: datetime.datetime
    """*DEPRECATED*"""
    high_score: int
    """The user's highest ever amount of eddies"""
    cull_warning: bool
    """*DEPRECATED*"""
    daily_minimum: int
    """The minimum amount of eddies the user is going to get each day"""
    supporter_type: SupporterType


class Better(TypedDict):
    user_id: int
    emoji: str
    first_bet: datetime.datetime
    last_bet: datetime.datetime
    points: int


class Option(TypedDict):
    val: str
    """The human outcome name"""


class Bet(TypedDict):
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
    betters: dict[str: Better]
    """A dict of user ID keys to their bet amounts"""
    result: Union[str, None]
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
    user_id: int
    """The discord user ID of the user who sent the message"""
    content: str
    """The reaction"""
    timestamp: datetime.datetime
    """When the reaction happened"""


class Reply(TypedDict):
    user_id: int
    """The discord user ID of the user who sent the reply"""
    content: str
    """The reply"""
    timestamp: datetime.datetime
    """When the reply happened"""
    message_id: str
    """The reply message ID"""


class Message(TypedDict):
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


class Thread(TypedDict):
    _id: ObjectId
    """The internal DB ID"""
    guild_id: int
    """The discord server ID of the server the thread is in"""
    thread_id: int
    """The discord thread ID of the thread"""
    name: str
    """Name of the thread"""
    created: datetime.datetime
    """When the thread was created"""
    owner: int
    """The discord user ID of the user who created the thread"""
    day: int
    """Only for SPOILER threads - the day a new ep comes out"""
    active: bool
    """Only for SPOILER threads - if we should still be posting spoiler warnings"""


class GuildDB(TypedDict):
    _id: ObjectId
    admins: list[int]
    guild_id: int
    created: datetime.datetime
    rename_king: datetime.datetime
    owner_id: int
    channel: int
    wordle: bool
    wordle_channel: int
    wordle_reminders: bool
    category: int
    role: int
    daily_minimum: int
    name: str
    tax_rate: float
    tax_rate_history: list[dict]
    king: int
    king_since: datetime.datetime
    king_history: list[dict]
    hash: str
    update_messages: bool
    revolution: bool
    supporter_role: int
    revolutionary_role: int
    pledged: list[int]
    release_ver: str
    release_notes: bool
    valorant_rollcall: bool
    valorant_channel: int
    valorant_role: int
    wordle_x_emoji: NotRequired[str]
    wordle_two_emoji: NotRequired[str]
    wordle_six_emoji: NotRequired[str]


class Reminder(TypedDict):
    _id: ObjectId
    guild_id: int
    created: datetime.datetime
    user_id: int
    timeout: datetime.datetime
    active: bool
    reason: str
    channel_id: int
    message_id: int
