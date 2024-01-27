"""Mocks for various discord classes."""

import dataclasses
import datetime


class MemberMock:
    def __init__(self, id: int, name: str = "some_name", mention: str = "some_mention") -> None:  # noqa: A002
        """Init."""
        self.id: int = id
        self.name: str = name
        self.mention: str = mention
        self.display_name = name

    async def send(self, content: str, silent: bool) -> None:
        """Mock the send method."""


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
    def __init__(self, guild_id: int, owner_id: int | None = None) -> None:
        """Init."""
        self._id = guild_id
        self._owner_id = owner_id if owner_id else 987654
        self._created_at = datetime.datetime.now()

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

    @staticmethod
    def get_member(member_id: int) -> MemberMock | None:
        """Mock for get_member."""
        if member_id == 0:
            return None
        return MemberMock(member_id, str(member_id))

    async def fetch_member(self, member_id: int) -> MemberMock | None:
        """Mock for fetch_member."""
        return self.get_member(member_id)


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
