"""Tests our UTC utility functions."""

import datetime

from discordbot.utilities import add_utc_offset, get_utc_offset, is_utc


class TestUTCFunctions:
    @staticmethod
    def test_get_utc_offset() -> None:
        """Tests getting the UTC offset."""
        offset = get_utc_offset()
        assert isinstance(offset, int)
        assert offset == 0

    @staticmethod
    def test_add_utc_offset() -> None:
        """Tests adding the offset."""
        now = datetime.datetime.now()
        now_utc = add_utc_offset(now)
        assert isinstance(now_utc, datetime.datetime)
        assert now == now_utc

    @staticmethod
    def test_is_utc() -> None:
        """Tests checking UTC."""
        now = datetime.datetime.now()
        assert is_utc(now)

        earlier = datetime.datetime.now() - datetime.timedelta(hours=1)
        assert not is_utc(earlier)
