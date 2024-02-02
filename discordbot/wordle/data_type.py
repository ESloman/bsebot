"""Wordle data type."""

import dataclasses
import datetime


@dataclasses.dataclass
class WordleSolve:
    """Dataclass for wordle."""

    solved: bool
    guesses: list[str]
    starting_word: str
    guess_count: int
    actual_word: str
    game_state: dict[int, dict[str, str | list]]
    timestamp: datetime.datetime
    share_text: str
    wordle_num: int
