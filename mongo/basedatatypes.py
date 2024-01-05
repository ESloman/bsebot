"""Holds our base dataclasses."""

from dataclasses import dataclass

from bson import ObjectId


@dataclass(frozen=True)
class BaseDBObject:
    """A class representing a base database object."""

    _id: ObjectId
    """The internal database ID."""
    guild_id: int
    """The discord guild/server ID."""


@dataclass(frozen=True)
class NamedDBObject(BaseDBObject):
    """A class that represents something in the database with a name."""

    name: str
    """The name of the object."""


@dataclass(frozen=True)
class ImplementsMessage:
    """A class that represents our database object contains a message ID."""

    channel_id: int
    """The discord ID of the channel the message is in."""
    message_id: int
    """The discord ID of the message."""
