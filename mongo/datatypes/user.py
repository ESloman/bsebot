"""Our UserDB datatypes."""

import dataclasses
import datetime

from discordbot.bot_enums import SupporterType
from mongo.datatypes.actions import ActivityDB, TransactionDB
from mongo.datatypes.basedatatypes import NamedDBObject


@dataclasses.dataclass(frozen=True)
class UserDB(NamedDBObject):
    """Represents a user in the database."""

    # basic user information
    uid: int
    """The discord user ID."""

    # eddies stuff
    points: int
    """The amount of eddies the user has in the server."""
    king: bool = False
    """Whether the user is KING in the server."""
    daily_eddies: bool = False
    """Whether the user receives daily eddie messages."""
    daily_summary: bool = False
    """Whether the user receives the daily eddies summary message."""
    pending_points: int = dataclasses.field(default=0)
    """The number of eddies the user has on pending bets."""
    high_score: int = dataclasses.field(default=0)
    """The user's highest ever amount of eddies."""
    daily_minimum: int | None = None
    """The minimum amount of eddies the user is going to get each day."""
    supporter_type: SupporterType = SupporterType.NEUTRAL
    """The user's alignment."""
    inactive: bool = False
    """Whether the user has left the server or not."""

    # DEPRECATED
    transaction_history: list[TransactionDB] | None = dataclasses.field(default_factory=list)
    """*DEPRECATED*"""
    activity_history: list[ActivityDB] | None = dataclasses.field(default_factory=list)
    """*DEPCREATED*"""
    last_cull_time: datetime.datetime | None = None
    """*DEPRECATED*"""
    cull_warning: bool | None = None
    """*DEPRECATED*"""
