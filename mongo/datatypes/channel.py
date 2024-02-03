"""Our ChannelDB datatype."""

import dataclasses
import datetime

from mongo.datatypes.basedatatypes import NamedDBObject


@dataclasses.dataclass(frozen=True)
class ChannelDB(NamedDBObject):
    """A dict representing a guild channel."""

    channel_id: int
    """The channel ID."""
    type: int
    """The discord channel type."""
    created: datetime.datetime
    """When the channel was created."""
    category_id: int
    """The category the channel belongs to."""
    is_nsfw: bool = False
    """Whether the channel is NSFW or not."""
