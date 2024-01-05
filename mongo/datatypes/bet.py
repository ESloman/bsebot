"""Our various bet datatypes."""

import dataclasses
import datetime

from mongo.datatypes.basedatatypes import BaseDBObject, ImplementsMessage


@dataclasses.dataclass(frozen=True)
class OptionDB:
    """A dict representing an option in a bet."""

    val: str
    """The human outcome name."""


@dataclasses.dataclass(frozen=True)
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


@dataclasses.dataclass(frozen=True)
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
    options: list[str] = dataclasses.field(default=list)
    """List of option emojis."""
    option_vals: list[str] = dataclasses.field(default=list)
    """List of option values."""
    users: list[int] = dataclasses.field(default=list)
    """List of user IDs."""
    betters: dict[str, BetterDB] = dataclasses.field(default=dict)
    """A dict of user ID keys to their bet amounts."""
    result: str | None = None
    """The outcome of the bet."""
    option_dict: dict[str, OptionDB] = dataclasses.field(default=dict)
    """a dict of emoji keys to the human readable names."""
    private: bool = False
    """Whether the bet was made in a private channel."""
    closed: datetime.datetime | None = None
    """Date the bet was closed."""
    last_bet: datetime.datetime | None = None
    """When the last bet was."""
    winners: dict[str, int] | None = None
