"""Tests our dataclasses."""

import dataclasses

import pytest

from mongo.datatypes.actions import ActivityDB, TransactionDB
from mongo.datatypes.basedatatypes import BaseEventDB
from mongo.datatypes.bet import BetDB, BetterDB, OptionDB
from mongo.datatypes.customs import EmojiDB, StickerDB
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.message import MessageDB, ReactionDB, ReplyDB, VCInteractionDB, WordleMessageDB
from mongo.datatypes.reminder import ReminderDB
from mongo.datatypes.revolution import RevolutionEventDB, RevolutionEventUnFrozenDB
from mongo.datatypes.thread import ThreadDB
from mongo.datatypes.user import UserDB
from tests.mocks import dataclass_mocks

FROZEN_INSTANCE_ERROR_REGEX = r"cannot assign to field '\w*'"


class TestActionDB:
    @pytest.mark.parametrize("act", dataclass_mocks.get_activity_inputs())
    def test_activitydb_init(self, act: dict) -> None:
        """Tests our ActivityDB dataclass."""
        cls_fields = {f.name for f in dataclasses.fields(ActivityDB)}
        extras = {k: v for k, v in act.items() if k not in cls_fields}
        activity_db = ActivityDB(**{k: v for k, v in act.items() if k in cls_fields}, extras=extras)
        assert isinstance(activity_db, ActivityDB)
        for key in act:
            try:
                assert act[key] == getattr(activity_db, key)
            except AttributeError:
                if key in extras:
                    assert act[key] == extras[key]
                else:
                    raise
        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            activity_db.type = 10

    @pytest.mark.parametrize("transaction", dataclass_mocks.get_transaction_inputs())
    def test_transactiondb_init(self, transaction: dict) -> None:
        """Tests our TransactionDB dataclass."""
        cls_fields = {f.name for f in dataclasses.fields(TransactionDB)}
        extras = {k: v for k, v in transaction.items() if k not in cls_fields}
        transaction_db = TransactionDB(**{k: v for k, v in transaction.items() if k in cls_fields}, extras=extras)
        assert isinstance(transaction_db, TransactionDB)
        for key in transaction:
            try:
                assert transaction[key] == getattr(transaction_db, key) or transaction[key] == extras.get(key)
            except AttributeError:
                if key in extras:
                    assert transaction[key] == extras[key]
                else:
                    raise

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            transaction_db.type = 10


class TestBetDB:
    @pytest.mark.parametrize("option", dataclass_mocks.get_bet_option_inputs())
    def test_optiondb_init(self, option: dict) -> None:
        """Tests our OptionDB dataclass."""
        option_db = OptionDB(**option)
        assert isinstance(option_db, OptionDB)
        for key in option:
            assert option[key] == getattr(option_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            option_db.val = "100"

    @pytest.mark.parametrize("better", dataclass_mocks.get_bet_better_inputs())
    def test_betterdb_init(self, better: dict) -> None:
        """Tests our BetterDB dataclass."""
        better_db = BetterDB(**better)
        assert isinstance(better_db, BetterDB)
        for key in better:
            assert better[key] == getattr(better_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            better_db.points = 100

    @pytest.mark.parametrize("bet", dataclass_mocks.get_bet_inputs())
    def test_betdb_init(self, bet: dict) -> None:
        """Tests our BetDB dataclass."""
        bet_db = BetDB(**bet)
        assert isinstance(bet_db, BetDB)
        for key in bet:
            assert bet[key] == getattr(bet_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            bet_db.title = "100"


class TestEmojiDB:
    @pytest.mark.parametrize("emoji", dataclass_mocks.get_emoji_inputs())
    def test_emojidb_init(self, emoji: dict) -> None:
        """Tests our EmojiDB dataclass."""
        emoji_db = EmojiDB(**emoji)
        assert isinstance(emoji_db, EmojiDB)
        for key in emoji:
            assert emoji[key] == getattr(emoji_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            emoji_db.eid = 100


class TestGuildDB:
    @pytest.mark.parametrize("guild", dataclass_mocks.get_guild_inputs())
    def test_userdb_init(self, guild: dict) -> None:
        """Tests our UserDB dataclass."""
        guild_db = GuildDB(**guild)
        assert isinstance(guild_db, GuildDB)
        for key in guild:
            assert guild[key] == getattr(guild_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            guild_db.king = 100


class TestMessageDB:
    @pytest.mark.parametrize("message", dataclass_mocks.get_message_inputs())
    def test_messagedb_init(self, message: dict) -> None:
        """Tests our MessageDB dataclass."""
        message_db = MessageDB(**message)
        assert isinstance(message_db, MessageDB)
        for key in message:
            assert message[key] == getattr(message_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            message_db.content = ""

    @pytest.mark.parametrize("reply", dataclass_mocks.get_message_reply_inputs())
    def test_replydb_init(self, reply: dict) -> None:
        """Tests our ReplyDB dataclass."""
        reply_db = ReplyDB(**reply)
        assert isinstance(reply_db, ReplyDB)
        for key in reply:
            assert reply[key] == getattr(reply_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            reply_db.content = ""

    @pytest.mark.parametrize("reaction", dataclass_mocks.get_message_reaction_inputs())
    def test_reactiondb_init(self, reaction: dict) -> None:
        """Tests our ReactionDB dataclass."""
        reaction_db = ReactionDB(**reaction)
        assert isinstance(reaction_db, ReactionDB)
        for key in reaction:
            assert reaction[key] == getattr(reaction_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            reaction_db.content = ""

    @pytest.mark.parametrize("vc", dataclass_mocks.get_message_vc_inputs())
    def test_vcinteractiondb_init(self, vc: dict) -> None:
        """Tests our VCInteractionDB dataclass."""
        vc_db = VCInteractionDB(**vc)
        assert isinstance(vc_db, MessageDB)
        assert isinstance(vc_db, VCInteractionDB)
        for key in vc:
            assert vc[key] == getattr(vc_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            vc_db.content = ""

    @pytest.mark.parametrize("message", dataclass_mocks.get_message_wordle_inputs())
    def test_wordlemessagedb_init(self, message: dict) -> None:
        """Tests our WordleMessageDB dataclass."""
        message_db = MessageDB(**message)
        assert isinstance(message_db, MessageDB)
        for key in message:
            assert message[key] == getattr(message_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            message_db.content = ""

        wordle_message = WordleMessageDB(**dataclasses.asdict(message_db), guesses=5)
        assert isinstance(wordle_message, WordleMessageDB)
        assert isinstance(wordle_message, MessageDB)
        for key in message:
            assert message[key] == getattr(wordle_message, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            wordle_message.content = ""


class TestReminderDB:
    @pytest.mark.parametrize("reminder", dataclass_mocks.get_reminder_inputs())
    def test_userdb_init(self, reminder: dict) -> None:
        """Tests our ReminderDB dataclass."""
        reminder_db = ReminderDB(**reminder)
        assert isinstance(reminder_db, ReminderDB)
        for key in reminder:
            assert reminder[key] == getattr(reminder_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            reminder_db.points = 100


class TestRevolutionEventsDB:
    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_init(self, event: dict) -> None:
        """Tests our RevolutionEventDB dataclass."""
        event_db = RevolutionEventDB(**event)
        assert isinstance(event_db, RevolutionEventDB)
        assert isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == getattr(event_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            event_db.chance += 50

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutionunfrozendb(self, event: dict) -> None:
        """Tests our RevolutionEventUnFrozenDB dataclass."""
        event_db = RevolutionEventUnFrozenDB(**event)
        assert isinstance(event_db, RevolutionEventUnFrozenDB)
        assert not isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == getattr(event_db, key)

        # test the unfrozen-ness
        event_db.chance += 50

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_unfrozen(self, event: dict) -> None:
        """Tests our RevolutionEventDB dataclass and the ability to unfreeze it."""
        event_db = RevolutionEventDB(**event)
        assert isinstance(event_db, RevolutionEventDB)
        assert isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == getattr(event_db, key)

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


class TestStickerDB:
    @pytest.mark.parametrize("sticker", dataclass_mocks.get_sticker_inputs())
    def test_emojidb_init(self, sticker: dict) -> None:
        """Tests our EmojiDB dataclass."""
        sticker_db = StickerDB(**sticker)
        assert isinstance(sticker_db, StickerDB)
        for key in sticker:
            assert sticker[key] == getattr(sticker_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            sticker_db.stid = 100


class TestThreadDB:
    @pytest.mark.parametrize("thread", dataclass_mocks.get_thread_inputs())
    def test_userdb_init(self, thread: dict) -> None:
        """Tests our ThreadDB dataclass."""
        thread_db = ThreadDB(**thread)
        assert isinstance(thread_db, ThreadDB)
        for key in thread:
            assert thread[key] == getattr(thread_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            thread_db.name = "some name"


class TestUserDB:
    @pytest.mark.parametrize("user", dataclass_mocks.get_user_inputs())
    def test_userdb_init(self, user: dict) -> None:
        """Tests our UserDB dataclass."""
        user_db = UserDB(**user)
        assert isinstance(user_db, UserDB)
        for key in user:
            assert user[key] == getattr(user_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            user_db.points = 100
