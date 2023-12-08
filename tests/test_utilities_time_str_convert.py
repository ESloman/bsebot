from pytest import mark

from discordbot.utilities import convert_time_str


class TestUtilitiesConvertTimeStr:
    @mark.parametrize(
        "input,expected",
        [
            # seconds
            ("1s", 1),
            ("5s", 5),
            ("100s", 100),
            # minutes
            ("1m", 60),
            ("2m", 120),
            ("5m", 300),
            ("100m", 6000),
            # hours
            ("1h", 3600),
            ("3h", 10800),
            ("10h", 36000),
            # days
            ("1d", 86400),
            ("7d", 604800),
            ("25d", 2160000),
            # weeks
            ("1w", 604800),
            ("7w", 4233600),
        ],
    )
    def test_single_unit(self, input: str, expected: int):
        assert convert_time_str(input) == expected

    @mark.parametrize(
        "input,expected",
        [
            # two units
            ("5m10s", 310),
            ("1w2d", 777600),
            ("2d5h", 190800),
            ("2d57s", 172857),
            ("58w879h", 38242800),
            # three units
            ("1h30m100s", 5500),
            ("1w2d13h", 824400),
            ("6w1d10s", 3715210),
            # four units
            ("3d5h20m36s", 278436),
            ("32w10h30m50s", 19391450),
            # five units
            ("2w3d45h10m50s", 1631450),
        ],
    )
    def test_multi_unit(self, input: str, expected: int):
        assert convert_time_str(input) == expected
