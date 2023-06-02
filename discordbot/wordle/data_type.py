
import datetime

from dataclasses import dataclass


@dataclass
class WordleSolve:
    solved: bool
    guesses: list
    starting_word: str
    guess_count: int
    actual_word: str
    game_state: dict
    timestamp: datetime.datetime
    share_text: str
    wordle_num: int
