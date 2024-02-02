"""Our emoji and sticker datatypes."""

import datetime
from dataclasses import dataclass

from mongo.datatypes.basedatatypes import NamedDBObject


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
