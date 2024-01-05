"""Tests our dataclasses."""

import dataclasses

import pytest

from mongo.datatypes.bet import BetDB, BetterDB, OptionDB
from mongo.datatypes.user import UserDB
from tests.mocks import dataclass_mocks

FROZEN_INSTANCE_ERROR_REGEX = r"cannot assign to field '\w*'"


class TestUserDB:
    @pytest.mark.parametrize("user", dataclass_mocks.get_user_inputs())
    def test_userdb_init(self, user: dict) -> None:  # noqa: PLR6301
        """Tests our UserDB dataclass."""
        user_db = UserDB(**user)
        assert isinstance(user_db, UserDB)
        for key in user:
            assert user[key] == user_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            user_db.points = 100


class TestBetDB:
    @pytest.mark.parametrize("option", dataclass_mocks.get_bet_option_inputs())
    def test_optiondb_init(self, option: dict) -> None:  # noqa: PLR6301
        """Tests our OptionDB dataclass."""
        option_db = OptionDB(**option)
        assert isinstance(option_db, OptionDB)
        for key in option:
            assert option[key] == option_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            option_db.val = "100"

    @pytest.mark.parametrize("better", dataclass_mocks.get_bet_better_inputs())
    def test_betterdb_init(self, better: dict) -> None:  # noqa: PLR6301
        """Tests our BetterDB dataclass."""
        better_db = BetterDB(**better)
        assert isinstance(better_db, BetterDB)
        for key in better:
            assert better[key] == better_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            better_db.points = 100

    @pytest.mark.parametrize("bet", dataclass_mocks.get_bet_inputs())
    def test_betdb_init(self, bet: dict) -> None:  # noqa: PLR6301
        """Tests our BetDB dataclass."""
        bet_db = BetDB(**bet)
        assert isinstance(bet_db, BetDB)
        for key in bet:
            assert bet[key] == bet_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            bet_db.title = "100"
