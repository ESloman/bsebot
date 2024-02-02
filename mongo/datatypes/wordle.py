"""Our wordle datatypes."""

import dataclasses
import datetime

from mongo.datatypes.basedatatypes import BaseDBObject, GuildedDBObject


@dataclasses.dataclass(frozen=True)
class WordleAttemptDB(GuildedDBObject):
    """Represents a wordle attempt in the database."""

    solved: bool
    """Whether the wordle was solved or not."""
    starting_word: str
    """The starting word we attempted the solve with."""
    actual_word: str
    """The solved word."""
    guesses: list[str]
    """The list of guesses."""
    guess_count: int
    """The number of guesses."""
    game_state: dict[int, dict[str, str | list]]
    """The game state."""
    timestamp: datetime.datetime
    """When we attempted the wordle."""
    share_text: str
    """The wordle share text we generated."""
    wordle_num: int
    """The wordle number."""


@dataclasses.dataclass(frozen=True)
class WordleReminderDB(BaseDBObject):
    """Represents a wordle reminder in the database."""

    name: str
    """The reminder text for the wordle reminder."""
    created_by: int
    """The ID of the discord user that created this wordle reminder."""
    created: datetime.datetime
    """When this wordle reminder was created."""
    archived: bool = False
    """Whether this wordle reminder has been archived or not."""
