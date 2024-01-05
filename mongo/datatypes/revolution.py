"""Our revolution datatypes."""

import dataclasses
import datetime

from bson import ObjectId

from mongo.datatypes.basedatatypes import BaseEventDB


@dataclasses.dataclass(kw_only=True)
class RevolutionEventUnFrozenDB:
    """Unfrozen variant for editing."""

    _id: ObjectId
    """The internal database ID."""
    guild_id: int
    """The discord guild/server ID."""
    channel_id: int
    """The discord ID of the channel the message is in."""
    message_id: int
    """The discord ID of the message."""
    type: str  # noqa: A003
    """Event type."""
    event_id: str
    """The event ID."""
    created: datetime.datetime
    """When the event was created."""
    expired: datetime.datetime
    """When the event will expire and 'resolve'."""
    open: bool  # noqa: A003
    """whether the event is still open."""
    king: int
    """The king the event affects."""
    chance: int
    """The chance of success."""
    locked_in_eddies: int | None = None
    """Number of eddies the King had when the event triggered."""
    points_distributed: int | None = None
    """The number of eddies given out if the event succeeds."""
    success: bool | None = None
    """Whether the event was a success or not."""
    times_saved: int = 0
    """Number of times the king tried to save themselves."""
    one_hour: bool = False
    """Whether the one hour warning was triggered."""
    quarter_hour: bool = False
    """Whether the 15 minute warning was triggered."""

    # users
    users: list[int] = dataclasses.field(default_factory=list)
    """everyone who's subscribed to the event."""
    supporters: list[int] = dataclasses.field(default_factory=list)
    """list of those supporting the event."""
    revolutionaries: list[int] = dataclasses.field(default_factory=list)
    """list of those revolutioning the event."""
    neutrals: list[int] = dataclasses.field(default_factory=list)
    """list of those impartial to the event."""
    locked: list[int] = dataclasses.field(default_factory=list)
    """Users who can't change their decision."""

    # deprecated
    ticket_cost: int | None = None
    """DEPRECATED"""
    ticket_buyers: list[int] | None = None
    """DEPRECATED"""
    eddies_spent: int | None = None
    """DEPRECATED"""


@dataclasses.dataclass(frozen=True)
class RevolutionEventDB(BaseEventDB):
    """A dict representing a revolution event."""

    def unfrozen(self) -> RevolutionEventUnFrozenDB:
        """Returns an unfrozen variant of the dataclass.

        Returns:
            RevolutionEventUnFrozenDB: the unfrozen dataclass
        """
        return RevolutionEventUnFrozenDB(**dataclasses.asdict(self))

    king: int
    """The king the event affects."""
    chance: int
    """The chance of success."""
    locked_in_eddies: int | None = None
    """Number of eddies the King had when the event triggered."""
    points_distributed: int | None = None
    """The number of eddies given out if the event succeeds."""
    success: bool | None = None
    """Whether the event was a success or not."""
    times_saved: int = 0
    """Number of times the king tried to save themselves."""
    one_hour: bool = False
    """Whether the one hour warning was triggered."""
    quarter_hour: bool = False
    """Whether the 15 minute warning was triggered."""

    # users
    users: list[int] = dataclasses.field(default_factory=list)
    """everyone who's subscribed to the event."""
    supporters: list[int] = dataclasses.field(default_factory=list)
    """list of those supporting the event."""
    revolutionaries: list[int] = dataclasses.field(default_factory=list)
    """list of those revolutioning the event."""
    neutrals: list[int] = dataclasses.field(default_factory=list)
    """list of those impartial to the event."""
    locked: list[int] = dataclasses.field(default_factory=list)
    """Users who can't change their decision."""

    # deprecated
    ticket_cost: int | None = None
    """DEPRECATED"""
    ticket_buyers: list[int] | None = None
    """DEPRECATED"""
    eddies_spent: int | None = None
    """DEPRECATED"""
