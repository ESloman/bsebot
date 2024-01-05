"""Tests our dataclasses."""

import dataclasses

import pytest

from mongo.datatypes.basedatatypes import BaseEventDB
from mongo.datatypes.bet import BetDB, BetterDB, OptionDB
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.revolution import RevolutionEventDB, RevolutionEventUnFrozenDB
from mongo.datatypes.thread import ThreadDB
from mongo.datatypes.user import UserDB
from tests.mocks import dataclass_mocks

FROZEN_INSTANCE_ERROR_REGEX = r"cannot assign to field '\w*'"


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


class TestGuildDB:
    @pytest.mark.parametrize("guild", dataclass_mocks.get_guild_inputs())
    def test_userdb_init(self, guild: dict) -> None:  # noqa: PLR6301
        """Tests our UserDB dataclass."""
        guild_db = GuildDB(**guild)
        assert isinstance(guild_db, GuildDB)
        for key in guild:
            assert guild[key] == guild_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            guild_db.king = 100


class TestRevolutionEventsDB:
    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_init(self, event: dict) -> None:  # noqa: PLR6301
        """Tests our RevolutionEventDB dataclass."""
        event_db = RevolutionEventDB(**event)
        assert isinstance(event_db, RevolutionEventDB)
        assert isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == event_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            event_db.chance += 50

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutionunfrozendb(self, event: dict) -> None:  # noqa: PLR6301
        """Tests our RevolutionEventUnFrozenDB dataclass."""
        event_db = RevolutionEventUnFrozenDB(**event)
        assert isinstance(event_db, RevolutionEventUnFrozenDB)
        assert not isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == event_db.__getattribute__(key)

        # test the unfrozen-ness
        event_db.chance += 50

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_unfrozen(self, event: dict) -> None:  # noqa: PLR6301
        """Tests our RevolutionEventDB dataclass and the ability to unfreeze it."""
        event_db = RevolutionEventDB(**event)
        assert isinstance(event_db, RevolutionEventDB)
        assert isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == event_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            event_db.chance += 50

        # now convert it to unfrozen
        unfrozen = event_db.unfrozen()
        unfrozen.chance += 50
        assert not isinstance(unfrozen, RevolutionEventDB)
        assert not isinstance(unfrozen, BaseEventDB)
        assert isinstance(unfrozen, RevolutionEventUnFrozenDB)
        assert unfrozen.chance != event_db.chance


class TestThreadDB:
    @pytest.mark.parametrize("thread", dataclass_mocks.get_thread_inputs())
    def test_userdb_init(self, thread: dict) -> None:  # noqa: PLR6301
        """Tests our ThreadDB dataclass."""
        thread_db = ThreadDB(**thread)
        assert isinstance(thread_db, ThreadDB)
        for key in thread:
            assert thread[key] == thread_db.__getattribute__(key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            thread_db.name = "some name"


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
