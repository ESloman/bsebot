"""Tests the BetManager class."""

import datetime
from unittest.mock import patch

import pytest

from discordbot.betmanager import BetManager
from mongo.bsepoints.points import UserPoints
from mongo.datatypes.bet import BetDB
from tests.mocks import bet_manager_mocks, interface_mocks


class TestBetManager:
    """Tests our BetManager class."""

    @pytest.fixture(autouse=True)
    def _test_data(self) -> None:
        """Test data."""

    def test_init(self) -> None:
        """Tests that we can initialise the class."""
        bet_manager = BetManager()
        assert isinstance(bet_manager, BetManager)

    @pytest.mark.parametrize(
        ("total_bet", "winning_total", "options_num", "losers"),
        [
            (100, 50, 2, 0),
            (5000, 4000, 4, 2),
            (10000, 0, 4, 4),
            (20000, 20000, 4, 0),
            (20000, 5000, 2, 10),
            (0, 0, 2, 0),
        ],
    )
    def test_calculate_bet_modifiers(self, total_bet: int, winning_total: int, options_num: int, losers: int) -> None:
        """Tests our 'calculate_bet_modifiers'."""
        bet_manager = BetManager()
        mult, coef = bet_manager.calculate_bet_modifiers(total_bet, winning_total, options_num, losers)
        assert isinstance(mult, float) or mult == 0
        assert isinstance(coef, float)
        assert -1 < mult < 1
        assert coef >= 1.2

    @pytest.mark.parametrize(
        ("points_bet", "multiplier", "coeff", "extra", "winners", "value"),
        [
            (100, -0.001, 2.1, 1000, 3, 533),
            (1000, -0.002, 2.2, 500, 2, 451),
            (500, -0.00005, 2.3, 0, 2, 1138),
        ],
    )
    def test_calculate_single_bet_winnings(
        self, points_bet: int, multiplier: float, coeff: float, extra: int, winners: int, value: int
    ) -> None:
        """Tests our '_calculate_single_bet_winnings'."""
        bet_manager = BetManager()
        points_won = bet_manager._calculate_single_bet_winnings(points_bet, multiplier, coeff, extra, winners)
        print(points_won)
        assert isinstance(points_won, int)
        assert points_won == value

    @pytest.mark.parametrize(
        ("supporter_type", "tax", "actual_won", "points_won", "expected"),
        [
            (0, (0.2, 0.1), 800, 1000, (840, 160)),
            (1, (0.2, 0.1), 800, 1000, (920, 80)),
            (0, (0.5, 0.1), 800, 1000, (600, 400)),
            (1, (0.5, 0.1), 800, 1000, (920, 80)),
            (0, (0.25, 0.1), 500, 1000, (875, 125)),
            (1, (0.25, 0.1), 500, 1000, (950, 50)),
        ],
    )
    def test_calculate_taxed_winnings(
        self, supporter_type: float, tax: int, actual_won: int, points_won: int, expected: tuple[int, int]
    ) -> None:
        """Tests our '_calculate_taxed_winnings'."""
        bet_manager = BetManager()
        _user = interface_mocks.query_mock("userpoints", {})[0]
        _user["supporter_type"] = supporter_type
        user = UserPoints.make_data_class(_user)
        with patch.object(bet_manager.user_points, "find_user", return_value=user):
            result = bet_manager._calculate_taxed_winnings(user.uid, user.guild_id, tax, actual_won, points_won)
        assert isinstance(result, tuple)
        assert result == expected

    def test_process_bet_winner(self) -> None:
        """Tests our _process_bet_winner."""
        bet_manager = BetManager()
        with patch.object(bet_manager.user_points, "increment_points", new=lambda *args, **kwargs: None):  # noqa: ARG005
            bet_manager._process_bet_winner("123", 123, "456", 100)

    @pytest.mark.parametrize(
        "test_bet",
        [
            bet_manager_mocks.get_bet_dict(0),
            bet_manager_mocks.get_bet_dict(1),
        ],
    )
    def test_close_a_bet(self, test_bet: BetDB) -> None:
        """Tests our 'close_a_bet'."""
        bet_manager = BetManager()

        _user = interface_mocks.query_mock("userpoints", {})[0]
        _user["supporter_type"] = 0 if int(test_bet.guild_id) < 900 else 1
        user = UserPoints.make_data_class(_user)

        # SO MANY MOCKS
        with (
            patch.object(bet_manager.user_bets, "get_bet_from_id", new=lambda _g, _b: test_bet),  # noqa: ARG005
            patch.object(bet_manager.user_bets, "close_a_bet", new=lambda _b, _e: None),  # noqa: ARG005
            patch.object(bet_manager.guilds, "get_tax_rate", new=lambda _g: (0.2, 0.1)),  # noqa: ARG005
            patch.object(bet_manager.user_points, "increment_points", new=lambda *args, **kwargs: None),  # noqa: ARG005
            patch.object(
                bet_manager.user_points,
                "find_user",
                return_value=user,
            ),
            patch.object(bet_manager.guilds, "get_king", new=lambda _g: 567),  # noqa: ARG005
            patch.object(bet_manager.user_bets, "update", new=lambda _b, _e: None),  # noqa: ARG005
        ):
            result = bet_manager.close_a_bet("123", 456, [":one:"])
            assert isinstance(result, dict)
            assert isinstance(result["result"], list)
            assert isinstance(result["outcome_name"], list)
            assert isinstance(result["timestamp"], datetime.datetime)
            assert isinstance(result["losers"], dict)
            assert isinstance(result["winners"], dict)
