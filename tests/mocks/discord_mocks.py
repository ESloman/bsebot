"""Mocks for various discord classes."""

import dataclasses
import datetime

from tests.mocks import interface_mocks


class MemberMock:
    def __init__(self, id: int, name: str = "some_name", mention: str = "some_mention") -> None:  # noqa: A002
        """Init."""
        self.id: int = id
        self.name: str = name
        self.mention: str = mention
        self.display_name = name

    async def send(self, content: str, silent: bool) -> None:
        """Mock the send method."""

    @property
    def bot(self) -> bool:
        """Bot property."""
        return False

    @property
    def nick(self) -> str:
        """Nickname property."""
        return self.display_name


@dataclasses.dataclass
class RoleMock:
    id: int
    name: str
    mention: str


class ChannelMock:
    def __init__(self, channel_id: int) -> None:
        """Init."""
        self._id: int = channel_id
        self._archived: bool = False

    @property
    def id(self) -> int:
        """ID property."""
        return self._id

    @property
    def archived(self) -> bool:
        """Archived property."""
        return self._archived

    async def send(self, *args, **kwargs) -> None:
        """Mocks the send method."""


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

    @staticmethod
    def get_member(member_id: int) -> MemberMock | None:
        """Mock for get_member."""
        if member_id == 0:
            return None
        return MemberMock(member_id, str(member_id))

    async def fetch_member(self, member_id: int) -> MemberMock | None:
        """Mock for fetch_member."""
        return self.get_member(member_id)

    def fetch_members(self):
        """Mock for fetch_memebers."""
        members = interface_mocks.query_mock("userpoints", {"guild_id": self.id})
        member_list = [MemberMock(member["uid"], member["name"]) for member in members]

        class FlattenAbleList:
            def __init__(self, things: list[MemberMock]) -> None:
                """Init."""
                self.things = things

            async def flatten(self) -> list[MemberMock]:
                return self.things

        return FlattenAbleList(member_list)


class MessageMock:
    def __init__(self, content: str = "", guild_id: int = 123) -> None:
        """Init."""
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
    def channel(self) -> ChannelMock:
        """Channel property."""
        return self._channel

    async def add_reaction(self, reaction: str) -> None:
        """Mock add_reaction."""
