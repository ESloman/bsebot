"""Our GuildDB datatype."""

import dataclasses
import datetime

from mongo.datatypes.basedatatypes import NamedDBObject


@dataclasses.dataclass(frozen=True)
class GuildDB(NamedDBObject):
    """A dict representing a guild/server."""

    # general server info
    owner_id: int
    """The ID of the user that owns the server."""
    created: datetime.datetime | None = None
    """When the server was created."""
    admins: list[int] = dataclasses.field(default_factory=list)
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
    tax_rate_history: list[dict[str, any]] = dataclasses.field(default_factory=list)
    """The tax rate history."""
    last_salary_time: datetime.datetime | None = None
    """The last time a salary event was triggered for this guild."""

    # KING stuff
    role: int | None = None
    """The role ID for the KING role."""
    king: int | None = None
    """The user ID of the user that is currently KING."""
    king_since: datetime.datetime | None = None
    """Start time of the current KING's rule."""
    king_history: list[dict[str, any]] = dataclasses.field(default_factory=list)
    """The KING history."""
    rename_king: datetime.datetime | None = None
    """When the King was last renamed."""
    rename_supporter: datetime.datetime | None = None
    """When the supporter role was last renamed."""
    rename_revolutionary: datetime.datetime | None = None
    """When the revolutionary role was last renamed."""
    revolution: bool = False
    """Whether revolution is enabled."""
    supporter_role: int | None = None
    """The ID of the role for supporters."""
    revolutionary_role: int | None = None
    """The ID of the role for revolutionaries."""
    pledged: list[int] = dataclasses.field(default_factory=list)
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
    hash: str | None = None
    """The last git hash."""
    release_ver: str | None = None
    """The last version of release notes published."""
    release_notes: bool = False
    """Whether to post release notes."""
    update_messages: bool = False
    """Whether to post bot update messages."""
