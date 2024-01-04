"""Mock for other random things."""

from dataclasses import dataclass


@dataclass
class MockDateTime:
    hour: float
    minute: float


def datetime_now(hour: int, minute: int) -> MockDateTime:
    """Mock datetime.datetime.now."""
    return MockDateTime(hour, minute)
