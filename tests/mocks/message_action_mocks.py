"""Mocks for message actions."""


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
