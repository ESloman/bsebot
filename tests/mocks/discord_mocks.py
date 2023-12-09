"""Mocks for various discord classes."""

import dataclasses


@dataclasses.dataclass
class MemberMock:
    id: int  # noqa: A003
    name: str = "some_name"


class GuildMock:
    @property
    def id(self) -> int:  # noqa: A003
        """ID property."""
        return 12345

    @staticmethod
    def get_member(member_id: int) -> MemberMock | None:
        """Mock for get_member."""
        if member_id == 0:
            return None
        return MemberMock(member_id, str(member_id))
