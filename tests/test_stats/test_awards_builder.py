"""Tests the AwardsBuilder class."""

import pytest

from discordbot.stats.awardsbuilder import AwardsBuilder
from discordbot.utilities import PlaceHolderLogger
from tests.mocks.bsebot_mocks import BSEBotMock


class TestAwardsBuilderStatics:
    """Tests the Awards Builder static methods."""

    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        """Setup fixture."""
        self.client = BSEBotMock()
        self.logger = PlaceHolderLogger

    @pytest.mark.parametrize(
        ("old", "new", "expected"),
        [
            (100, 120, " (up `20.0%`)"),
            (100, 100, " (no change)"),
            (100, 80, " (down `20.0%`)"),
        ],
    )
    def test_get_comparison_string(self, old: float, new: float, expected: str) -> None:
        """Tests getting the comparison string function."""
        awards_builder = AwardsBuilder(self.client, 123456, self.logger)
        comp_string = awards_builder._get_comparison_string(new, old)
        assert expected == comp_string
