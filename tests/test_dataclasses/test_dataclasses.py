"""Tests our dataclasses."""

import dataclasses

import pytest

from mongo.datatypes.actions import ActivityDB, TransactionDB
from mongo.datatypes.autogeneratedbets import AutoGeneratedBetDB
from mongo.datatypes.basedatatypes import BaseEventDB
from mongo.datatypes.bet import BetDB, BetterDB, OptionDB
from mongo.datatypes.botactivities import BotActivityDB
from mongo.datatypes.channel import ChannelDB
from mongo.datatypes.customs import EmojiDB, StickerDB
from mongo.datatypes.guild import GuildDB
from mongo.datatypes.message import MessageDB, ReactionDB, ReplyDB, VCInteractionDB, WordleMessageDB
from mongo.datatypes.revolution import RevolutionEventDB, RevolutionEventUnFrozenDB
from mongo.datatypes.thread import ThreadDB
from mongo.datatypes.user import UserDB
from mongo.datatypes.wordle import WordleReminderDB
from tests.mocks import dataclass_mocks

FROZEN_INSTANCE_ERROR_REGEX = r"cannot assign to field '\w*'"


class TestActionDB:
    """Tests our activity and transaction datatypes."""

    @pytest.mark.parametrize("act", dataclass_mocks.get_activity_inputs())
    def test_activitydb_init(self, act: dict[str, any]) -> None:
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
    def test_transactiondb_init(self, transaction: dict[str, any]) -> None:
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


class TestAutoGeneratedDB:
    """Tests our autogenerated bets datatpes."""

    @pytest.mark.parametrize("bet", dataclass_mocks.get_autobet_inputs())
    def test_autogeneratedbetdb_init(self, bet: dict[str, any]) -> None:
        """Tests our AutoGeneratedBetDB dataclass."""
        bet_db = AutoGeneratedBetDB(**bet)
        assert isinstance(bet_db, AutoGeneratedBetDB)
        for key in bet:
            assert bet[key] == getattr(bet_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            bet_db.title = "some other title"


class TestBetDB:
    """Tests our bet datatypes."""

    @pytest.mark.parametrize("option", dataclass_mocks.get_bet_option_inputs())
    def test_optiondb_init(self, option: dict[str, any]) -> None:
        """Tests our OptionDB dataclass."""
        option_db = OptionDB(**option)
        assert isinstance(option_db, OptionDB)
        for key in option:
            assert option[key] == getattr(option_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            option_db.val = "100"

    @pytest.mark.parametrize("better", dataclass_mocks.get_bet_better_inputs())
    def test_betterdb_init(self, better: dict[str, any]) -> None:
        """Tests our BetterDB dataclass."""
        better_db = BetterDB(**better)
        assert isinstance(better_db, BetterDB)
        for key in better:
            assert better[key] == getattr(better_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            better_db.points = 100

    @pytest.mark.parametrize("bet", dataclass_mocks.get_bet_inputs())
    def test_betdb_init(self, bet: dict[str, any]) -> None:
        """Tests our BetDB dataclass."""
        bet_db = BetDB(**bet)
        assert isinstance(bet_db, BetDB)
        for key in bet:
            assert bet[key] == getattr(bet_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            bet_db.title = "100"


class TestBotActvityDB:
    """Tests our bot activity datatpes."""

    @pytest.mark.parametrize("activity", dataclass_mocks.get_bot_activity_inputs())
    def test_bot_activity_db(self, activity: dict[str, any]) -> None:
        """Tests our BotActivityDB dataclass."""
        activity_db = BotActivityDB(**activity)
        assert isinstance(activity_db, BotActivityDB)
        for key in activity:
            assert activity[key] == getattr(activity_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            activity_db.name = "some other title"


class TestChannelDB:
    """Tests our channel datatypes."""

    @pytest.mark.parametrize("channel", dataclass_mocks.get_channel_inputs())
    def test_channeldb_init(self, channel: dict[str, any]) -> None:
        """Tests our ChannelDB dataclass."""
        channel_db = ChannelDB(**channel)
        assert isinstance(channel_db, ChannelDB)
        for key in channel:
            assert channel[key] == getattr(channel_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            channel_db.name = ""


class TestEmojiDB:
    """Tests our emoji datatypes."""

    @pytest.mark.parametrize("emoji", dataclass_mocks.get_emoji_inputs())
    def test_emojidb_init(self, emoji: dict[str, any]) -> None:
        """Tests our EmojiDB dataclass."""
        emoji_db = EmojiDB(**emoji)
        assert isinstance(emoji_db, EmojiDB)
        for key in emoji:
            assert emoji[key] == getattr(emoji_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            emoji_db.eid = 100


class TestGuildDB:
    """Tests our guild datatypes."""

    @pytest.mark.parametrize("guild", dataclass_mocks.get_guild_inputs())
    def test_userdb_init(self, guild: dict[str, any]) -> None:
        """Tests our UserDB dataclass."""
        guild_db = GuildDB(**guild)
        assert isinstance(guild_db, GuildDB)
        for key in guild:
            assert guild[key] == getattr(guild_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            guild_db.king = 100


class TestMessageDB:
    """Tests our message datatypes."""

    @pytest.mark.parametrize("message", dataclass_mocks.get_message_inputs())
    def test_messagedb_init(self, message: dict[str, any]) -> None:
        """Tests our MessageDB dataclass."""
        message_db = MessageDB(**message)
        assert isinstance(message_db, MessageDB)
        for key in message:
            assert message[key] == getattr(message_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            message_db.content = ""

    @pytest.mark.parametrize("reply", dataclass_mocks.get_message_reply_inputs())
    def test_replydb_init(self, reply: dict[str, any]) -> None:
        """Tests our ReplyDB dataclass."""
        reply_db = ReplyDB(**reply)
        assert isinstance(reply_db, ReplyDB)
        for key in reply:
            assert reply[key] == getattr(reply_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            reply_db.content = ""

    @pytest.mark.parametrize("reaction", dataclass_mocks.get_message_reaction_inputs())
    def test_reactiondb_init(self, reaction: dict[str, any]) -> None:
        """Tests our ReactionDB dataclass."""
        reaction_db = ReactionDB(**reaction)
        assert isinstance(reaction_db, ReactionDB)
        for key in reaction:
            assert reaction[key] == getattr(reaction_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            reaction_db.content = ""

    @pytest.mark.parametrize("vc", dataclass_mocks.get_message_vc_inputs())
    def test_vcinteractiondb_init(self, vc: dict[str, any]) -> None:
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
    def test_wordlemessagedb_init(self, message: dict[str, any]) -> None:
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


class TestRevolutionEventsDB:
    """Tests our revolution event datatypes."""

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_init(self, event: dict[str, any]) -> None:
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
    def test_revolutionunfrozendb(self, event: dict[str, any]) -> None:
        """Tests our RevolutionEventUnFrozenDB dataclass."""
        event_db = RevolutionEventUnFrozenDB(**event)
        assert isinstance(event_db, RevolutionEventUnFrozenDB)
        assert not isinstance(event_db, BaseEventDB)
        for key in event:
            assert event[key] == getattr(event_db, key)

        # test the unfrozen-ness
        event_db.chance += 50

    @pytest.mark.parametrize("event", dataclass_mocks.get_revolution_inputs())
    def test_revolutiondb_unfrozen(self, event: dict[str, any]) -> None:
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
    """Test our sticker datatypes."""

    @pytest.mark.parametrize("sticker", dataclass_mocks.get_sticker_inputs())
    def test_emojidb_init(self, sticker: dict[str, any]) -> None:
        """Tests our EmojiDB dataclass."""
        sticker_db = StickerDB(**sticker)
        assert isinstance(sticker_db, StickerDB)
        for key in sticker:
            assert sticker[key] == getattr(sticker_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            sticker_db.stid = 100


class TestThreadDB:
    """Test our thread datatypes."""

    @pytest.mark.parametrize("thread", dataclass_mocks.get_thread_inputs())
    def test_userdb_init(self, thread: dict[str, any]) -> None:
        """Tests our ThreadDB dataclass."""
        thread_db = ThreadDB(**thread)
        assert isinstance(thread_db, ThreadDB)
        for key in thread:
            assert thread[key] == getattr(thread_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            thread_db.name = "some name"


class TestUserDB:
    """Tests our user datatypes."""

    @pytest.mark.parametrize("user", dataclass_mocks.get_user_inputs())
    def test_userdb_init(self, user: dict[str, any]) -> None:
        """Tests our UserDB dataclass."""
        user_db = UserDB(**user)
        assert isinstance(user_db, UserDB)
        for key in user:
            assert user[key] == getattr(user_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            user_db.points = 100


class TestWordleDB:
    """Tests our Wordle datatypes."""

    @pytest.mark.parametrize("wordle_reminder", dataclass_mocks.get_wordle_reminder_inputs())
    def test_wordlereminderdb_init(self, wordle_reminder: dict[str, any]) -> None:
        """Tests our UserDB dataclass."""
        wordle_reminder_db = WordleReminderDB(**wordle_reminder)
        assert isinstance(wordle_reminder_db, WordleReminderDB)
        for key in wordle_reminder:
            assert wordle_reminder[key] == getattr(wordle_reminder_db, key)

        # test the frozen-ness
        with pytest.raises(dataclasses.FrozenInstanceError, match=FROZEN_INSTANCE_ERROR_REGEX):
            wordle_reminder_db.name = "Some other name"
