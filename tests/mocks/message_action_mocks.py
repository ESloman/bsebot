"""Mocks for message actions."""

import datetime

from bson import ObjectId
from pymongo.errors import OperationFailure

from mongo.datatypes.message import MessageDB


def query_tough_day_exc(query: dict) -> None:
    """Mock for tough day query."""
    raise OperationFailure("")


def query_tough_day_exc_sec(query: dict) -> None | list[dict]:
    """Mock for tough day query."""
    if not query["is_bot"]:
        return [
            MessageDB(
                123456,
                123456,
                ObjectId(),
                123456,
                123456,
                datetime.datetime.now(),
                "6/6",
                ["message", "wordle"],
            )
            for _ in range(4)
        ]
    raise OperationFailure("")


def get_wordle_squares_content() -> list[tuple[str, str | None]]:
    """Returns a bunch of wordle strings to use as content for square reactions."""
    return [
        (
            """Wordle 934 3/6

    ⬛⬛⬛⬛🟨
    ⬛⬛⬛🟩🟨
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 934 6/6

    ⬛🟩⬛⬛⬛
    ⬛🟨⬛⬛🟨
    🟨🟩⬛🟩🟨
    ⬛🟩🟩🟩🟩
    ⬛🟩🟩🟩🟩
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟨⬛⬛
    ⬛🟨🟨🟨⬛
    ⬛🟨⬛🟨🟨
    🟩🟩🟩🟩🟩""",
            "🟨",
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟨⬛⬛
    ⬛🟨🟨⬛⬛
    ⬛⬛⬛🟨🟨
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟩⬛⬛
    ⬛🟩🟩🟩⬛
    ⬛🟩⬛🟩🟩
    🟩🟩🟩🟩🟩""",
            "🟩",
        ),
    ]


def get_wordle_symmetry_content() -> list[tuple[str, str | None]]:
    """Returns a bunch of wordle strings to use as content for symmetry reactions."""
    return [
        (
            """Wordle 934 3/6

⬛⬛⬛⬛🟨
⬛⬛⬛🟩🟨
🟩🟩🟩🟩🟩""",
            False,
        ),
        (
            """Wordle 934 6/6

⬛🟩⬛⬛⬛
⬛🟨⬛⬛🟨
🟨🟩⬛🟩🟨
⬛🟩🟩🟩🟩
⬛🟩🟩🟩🟩
🟩🟩🟩🟩🟩""",
            False,
        ),
        (
            """Wordle 934 3/6

🟨⬛⬛⬛🟨
🟨🟩⬛🟩🟨
🟩🟩🟩🟩🟩""",
            True,
        ),
        (
            """Wordle 934 5/6

🟨⬛⬛⬛🟨
🟨🟩⬛🟩🟨
🟨🟩⬛🟩🟨
🟨🟩🟩⬛🟨
🟩🟩🟩🟩🟩""",
            False,
        ),
        (
            """Wordle 934 5/6

⬛⬛⬛⬛⬛
⬛🟩⬛🟩⬛
🟨🟩⬛🟩🟨
🟨⬛🟩⬛🟨
🟩🟩🟩🟩🟩""",
            True,
        ),
        (
            """Wordle 934 X/6

⬛⬛⬛⬛⬛
⬛🟩⬛🟩⬛
🟨🟩⬛🟩🟨
🟨⬛🟩⬛🟨
⬛🟩🟩🟩⬛
🟨🟩🟩🟩🟨""",
            True,
        ),
        (
            """Wordle 934 5/6

        ⬛⬛⬛⬛⬛
        ⬛🟩⬛🟩⬛
        🟨🟩⬛🟩🟨
        🟨⬛🟩⬛🟨
        🟩🟩🟩🟩🟩""",
            True,
        ),
    ]


def get_wordle_run_content() -> list[str]:
    """Returns a bunch of wordle strings to use as content for run command."""
    return [
        (
            """Wordle 934 3/6

    ⬛⬛⬛⬛🟨
    ⬛⬛⬛🟩🟨
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟨⬛⬛
    ⬛🟨🟨🟨⬛
    ⬛🟨⬛🟨🟨
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟨⬛⬛
    ⬛🟨🟨⬛⬛
    ⬛⬛⬛🟨🟨
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 4/6

    ⬛⬛🟩⬛⬛
    ⬛🟩🟩🟩⬛
    ⬛🟩⬛🟩🟩
    🟩🟩🟩🟩🟩""",
            None,
        ),
        (
            """Wordle 927 6/6

    ⬛⬛🟩⬛⬛
    ⬛🟩🟩🟩⬛
    ⬛🟩⬛🟩🟩
    ⬛🟩⬛🟩🟩
    ⬛🟩⬛🟩🟩
    🟩🟩🟩🟩🟩""",
            "😬",
        ),
        (
            """Wordle 927 X/6

    ⬛⬛🟩⬛⬛
    ⬛🟩🟩🟩⬛
    ⬛🟩⬛🟩🟩
    ⬛🟩⬛🟩🟩
    ⬛🟩⬛🟩🟩
    🟩🟩⬛🟩🟩""",
            "😞",
        ),
        (
            """Wordle 927 2/6

    ⬛⬛🟩⬛⬛
    🟩🟩🟩🟩🟩""",
            "🎉",
        ),
        (
            """Wordle 927 1/6

    🟩🟩🟩🟩🟩""",
            "🎉",
        ),
    ]
