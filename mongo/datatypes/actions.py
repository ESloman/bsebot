"""Various action datatypes."""

import dataclasses
import datetime

from discordbot.bot_enums import ActivityTypes, TransactionTypes
from mongo.datatypes.basedatatypes import BaseDBObject


@dataclasses.dataclass(frozen=True)
class ActivityDB(BaseDBObject):
    """A dict representing an activity."""

    uid: int
    """The ID of the user the activity relates to."""
    type: ActivityTypes
    """The type of activity."""
    timestamp: datetime.datetime
    """The time the activity took place."""
    comment: str = ""
    """The comment pertaining to the activity."""
    extras: dict | None = None
    """Any extra args passed."""


@dataclasses.dataclass(frozen=True)
class TransactionDB(BaseDBObject):
    """A dict representing a transaction."""

    uid: int
    """The ID of the user the transaction relates to."""
    type: TransactionTypes
    """The type of transaction."""
    timestamp: datetime.datetime
    """The time the transaction took place."""
    amount: int | None = None
    """The amount of eddies in the transaction."""
    comment: str = ""
    """The comment pertaining to a transaction."""
    bet_id: str | None = None
    """Bet ID of the transaction."""
    extras: dict | None = None
    """Any extra args passed."""
