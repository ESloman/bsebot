"""Mocks for various discord classes."""

import datetime
import random

import discord

from discordbot.constants import BSE_BOT_ID
from tests.mocks import interface_mocks


class MemberMock:
    def __init__(self, id: int, name: str = "some_name", mention: str = "some_mention") -> None:  # noqa: A002
        """Init."""
        self.id: int = id
        self.name: str = name
        self.mention: str = mention
        self.display_name = name
        self._bot = False

    async def send(self, *args, **kwargs) -> None:
        """Mock the send method."""

    @property
    def bot(self) -> bool:
        """Bot property."""
        return self._bot

    @property
    def nick(self) -> str:
        """Nickname property."""
        return self.display_name

    @property
    def roles(self) -> list:
        """Roles property."""
        return [RoleMock(123456 << x, "", "") for x in range(5)]

    @property
    def dm_channel(self) -> bool:
        """DM channel property."""
        return random.randint(0, 1) == 1

    async def remove_roles(self, *args, **kwargs) -> None:
        """Remove roles mock."""

    async def add_roles(self, *args, **kwargs) -> None:
        """Add roles mock."""

    async def create_dm(self, *args, **kwargs) -> None:
        """Create DM mock."""


class RoleMock:
    def __init__(self, _id: int = 123, name: str = "", mention: str = "") -> None:
        """Init."""
        self._id = _id
        self._name = name
        self._mention = mention

    @property
    def id(self) -> int:
        """ID property."""
        return self._id

    @property
    def name(self) -> int:
        """Name property."""
        return self._name

    @property
    def mention(self) -> int:
        """Mention property."""
        return self._mention

    @property
    def members(self) -> list[MemberMock]:
        """Members property."""
        _members = random.choices(interface_mocks.query_mock("userpoints", {}), k=3)
        return [MemberMock(member["uid"], member.get("name", ""), "") for member in _members]

    async def edit(self, *args, **kwargs) -> None:
        """Edit mock."""


class ChannelMock:
    def __init__(
        self,
        channel_id: int,
        name: str | None = None,
        created_at: datetime.datetime | None = None,
        owner_id: int = 123456,
        member_ids: list[int] | None = None,
    ) -> None:
        """Init."""
        self._id: int = channel_id
        self._name: str = name or ""
        self._created_at = created_at or datetime.datetime.now()
        self._owner_id = owner_id
        self._archived: bool = False
        self._threads: list[ThreadMock] = []
        self._type = discord.ChannelType.text
        self._member_ids = member_ids

    @property
    def id(self) -> int:
        """ID property."""
        return self._id

    @property
    def type(self) -> discord.ChannelType:
        """Type property."""
        return self._type

    @property
    def name(self) -> int:
        """Name property."""
        return self._name

    @property
    def created_at(self) -> datetime.datetime:
        """Created property."""
        return self._created_at

    @property
    def owner_id(self) -> int:
        """Owner ID property."""
        return self._owner_id

    @property
    def archived(self) -> bool:
        """Archived property."""
        return self._archived

    @property
    def threads(self) -> list:
        """Threads property."""
        return self._threads

    @property
    def members(self) -> list[MemberMock]:
        """Returns a list of members."""
        return [MemberMock(_id) for _id in self._member_ids] if self._member_ids else []

    async def send(self, *args, **kwargs):
        """Mocks the send method."""
        return MessageMock("", 123456, 6543210)

    async def fetch_message(self, message_id: int):
        """Fetch message mock."""
        return MessageMock("", message_id)

    def get_partial_message(self, message_id: int):
        """Get partial message mock."""
        return MessageMock("", message_id)

    async def trigger_typing(self) -> None:
        """Mock trigger typing."""


class ThreadMock(ChannelMock):
    def __init__(
        self,
        channel_id: int,
        name: str | None = None,
        created_at: datetime.datetime | None = None,
        owner_id: int = 123456,
    ) -> None:
        """Init."""
        super().__init__(channel_id, name, created_at, owner_id)
        self._add_bot_id: bool = False

    @property
    def locked(self) -> bool:
        """Locked property."""
        return self._archived

    async def join(self):
        """Mock join."""

    async def fetch_members(self):
        """Mock the fetching members."""
        members = interface_mocks.query_mock("userpoints", {"guild_id": self.id})
        if self._add_bot_id:
            members.append({"uid": BSE_BOT_ID, "name": "BSEBot"})
        return [MemberMock(member["uid"], member["name"]) for member in members]


class GuildMock:
    def __init__(self, guild_id: int, owner_id: int | None = None, name: str = "") -> None:
        """Init."""
        self._id = guild_id
        self._owner_id = owner_id if owner_id else 987654
        self._created_at = datetime.datetime.now()
        self._name = name

    @property
    def id(self) -> int:
        """ID property."""
        return self._id

    @property
    def owner_id(self) -> int:
        """Owner ID property."""
        return self._owner_id

    @property
    def created_at(self) -> datetime.datetime:
        """Created at property."""
        return self._created_at

    @property
    def name(self) -> str:
        """Name property."""
        return self._name

    @property
    def emojis(self) -> list:
        """Mock for emojis."""
        emojis = interface_mocks.query_mock("serveremojis", {"guild_id": self.id})
        emoji_list: list[EmojiMock] = [
            EmojiMock(
                emoji["eid"], emoji["name"], emoji["created"], MemberMock(emoji["created_by"]), GuildMock(self.id)
            )
            for emoji in emojis
        ]
        emoji_list[2].id = 654321
        return emoji_list

    @property
    def stickers(self) -> list:
        """Mock for stickers."""
        stickers = interface_mocks.query_mock("serverstickers", {"guild_id": self.id})
        sticker_list: list[StickerMock] = [
            StickerMock(
                sticker["stid"],
                sticker["name"],
                sticker["created"],
                MemberMock(sticker["created_by"]),
                GuildMock(self.id),
            )
            for sticker in stickers
        ]
        if len(sticker_list) > 2:
            sticker_list[1].id = 654321
        return sticker_list

    @staticmethod
    def get_member(member_id: int) -> MemberMock | None:
        """Mock for get_member."""
        if member_id == 0:
            return None
        return MemberMock(member_id, str(member_id))

    async def fetch_emoji(self, emoji_id: int):
        """Mock for fetch emoji."""
        emoji = interface_mocks.query_mock("serveremojis", {"guild_id": self.id, "eid": emoji_id})
        emoji = emoji[0] if emoji else None
        name = emoji["name"] if emoji else "some name"
        created = emoji["created"] if emoji else datetime.datetime.now()
        created_by = emoji["created_by"] if emoji else 123456
        return EmojiMock(emoji_id, name, created, MemberMock(created_by), GuildMock(self.id))

    async def fetch_sticker(self, sticker_id: int):
        """Mock for fetch sticker."""
        sticker = interface_mocks.query_mock("serverstickers", {"guild_id": self.id, "stid": sticker_id})
        sticker = sticker[0] if sticker else None
        name = sticker["name"] if sticker else "some name"
        created = sticker["created"] if sticker else datetime.datetime.now()
        created_by = sticker["created_by"] if sticker else 123456
        return StickerMock(sticker_id, name, created, MemberMock(created_by), GuildMock(self.id))

    async def fetch_member(self, member_id: int) -> MemberMock | None:
        """Mock for fetch_member."""
        return self.get_member(member_id)

    def fetch_members(self):
        """Mock for fetch_memebers."""
        members = interface_mocks.query_mock("userpoints", {"guild_id": self.id})
        member_list = [MemberMock(member["uid"], member["name"]) for member in members]

        if len(member_list) > 8:
            # change some info to test different things
            member_list[1]._bot = True
            member_list[2].id = 123456
            member_list[3].name = "something else"
            member_list[3].display_name = "something else"

        class FlattenAbleList:
            def __init__(self, things: list[MemberMock]) -> None:
                """Init."""
                self.things = things

            async def flatten(self) -> list[MemberMock]:
                return self.things

        return FlattenAbleList(member_list)

    async def fetch_channels(self):
        """Mock for fetch_channels."""
        interactions = interface_mocks.query_mock("userinteractions", {"guild_id": self.id})[-500:]
        channel_ids = {interaction["channel_id"] for interaction in interactions}
        threads = interface_mocks.query_mock("spoilerthreads", {"guild_id": self.id})[-5:]
        channels = [ChannelMock(channel_id) for channel_id in channel_ids]
        threads = [
            ThreadMock(thread["thread_id"], thread["name"], thread["created"], thread["owner"]) for thread in threads
        ]
        if len(threads) > 3:
            threads[1]._archived = True
            threads[2]._add_bot_id = True
            threads[3]._id = 654321
        channels[0]._threads = threads
        if len(channels) > 3:
            channels[2]._type = discord.ChannelType.voice
        return channels

    async def fetch_channel(self, _id: int):
        """Mock for fetch_channel."""
        return ChannelMock(_id)

    def get_role(self, role_id: int):
        """Mock for get role."""
        return RoleMock(role_id, "", "")


class EmojiMock:
    def __init__(self, eid: int, name: str, created_at: datetime.datetime, owner: MemberMock, guild: GuildMock) -> None:
        """Init."""
        self.id = eid
        self.name = name
        self.created_at = created_at
        self.user = owner
        self.guild = GuildMock


class StickerMock:
    def __init__(self, sid: int, name: str, created_at: datetime.datetime, owner: MemberMock, guild: GuildMock) -> None:
        """Init."""
        self.id = sid
        self.name = name
        self.created_at = created_at
        self.user = owner
        self.guild = GuildMock


class MessageMock:
    def __init__(self, content: str = "", guild_id: int = 123, message_id: int = 987654) -> None:
        """Init."""
        self._id = message_id
        self._content = content
        self._guild = GuildMock(guild_id)
        self._channel = ChannelMock(654321)

    @property
    def content(self) -> str:
        """Content property."""
        return self._content

    @property
    def guild(self) -> GuildMock:
        """Guild property."""
        return self._guild

    @property
    def id(self) -> int:
        """ID prpoerty."""
        return self._id

    @property
    def channel(self) -> ChannelMock:
        """Channel property."""
        return self._channel

    @property
    def jump_url(self) -> str:
        """Jump URL property."""
        return ""

    async def add_reaction(self, reaction: str) -> None:
        """Mock add_reaction."""

    async def edit(self, *args, **kwargs) -> None:
        """Mocks the edit method."""

    async def reply(self, *args, **kwargs) -> None:
        """Mocks the reply method."""


class FollowUpMock:
    @staticmethod
    async def defer(*args, **kwargs) -> None:
        """Mocks followup defer."""

    @staticmethod
    async def send(*args, **kwargs) -> None:
        """Mocks followup send."""

    @staticmethod
    async def edit_message(*args, **kwargs) -> None:
        """Mocks followup edit_message."""

    @staticmethod
    async def send_message(*args, **kwargs) -> None:
        """Mocks followup send message."""


class InteractionMock:
    def __init__(self, guild_id: int | None, user_id: int = 123456) -> None:
        """Init."""
        if guild_id is None:
            guild_id = 123456
        self._guild = GuildMock(guild_id)
        self._message = MessageMock("", guild_id)
        self._user = MemberMock(user_id)
        self._channel = ChannelMock(123456)

    @property
    def followup(self) -> FollowUpMock:
        """Mock followup property."""
        return FollowUpMock

    @property
    def response(self) -> FollowUpMock:
        """Mock response property."""
        return FollowUpMock

    @property
    def message(self) -> MessageMock:
        """Message property."""
        return self._message

    @property
    def guild(self) -> GuildMock:
        """Guild property."""
        return self._guild

    @property
    def guild_id(self) -> int:
        """Guild ID property."""
        return self._guild.id

    @property
    def user(self) -> MemberMock:
        """User property."""
        return self._user

    @property
    def user_id(self) -> int:
        """Guild ID property."""
        return self._user.id

    @property
    def channel(self) -> ChannelMock:
        """Channel property."""
        return self._channel


class ButtonMock:
    def __init__(self, label: str = "") -> None:
        """Init."""
        self._label = label

    @property
    def label(self) -> str:
        """Label property."""
        return self._label


class ContextMock:
    def __init__(self, guild_id: int, user_id: int = 123456) -> None:
        """Init."""
        self._guild_id: int = guild_id
        self._user = MemberMock(user_id)

    @property
    def guild_id(self) -> int:
        """Guild ID property."""
        return self._guild_id

    @property
    def user(self) -> MemberMock:
        """User property."""
        return self._user

    @property
    def followup(self) -> FollowUpMock:
        """Mock followup property."""
        return FollowUpMock

    @property
    def response(self) -> FollowUpMock:
        """Mock response property."""
        return FollowUpMock

    async def respond(self, *args, **kwargs) -> None:
        """Respond mock."""
