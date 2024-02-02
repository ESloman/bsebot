"""Mocks for mongo classes."""

import random

from bson import ObjectId

from mongo.datatypes.guild import GuildDB
from mongo.datatypes.user import UserDB


class MockClient:
    """Mock client class."""

    def __init__(self, *_args, **_kwargs) -> None:
        """Initialisation method."""

    def list_database_names(self) -> list[str]:
        """Mock list_database_names method."""
        return [
            "database_name",
            "another_database_name",
        ]


class MockDatabase:
    """Mock database class."""

    def __init__(self, *_args, **_kwargs) -> None:
        """Initialisation method."""

    def list_collection_names(self, include_system_collections: bool = False) -> list[str]:
        """Mock list_collection_names method."""
        return [
            "collection_name",
            "another_collecton_name",
        ]


class MockResult:
    """Mock result class."""

    def __init__(self, num: int) -> None:
        """Initialisation method."""
        self._ids = [ObjectId() for _ in range(num)]

    @property
    def inserted_ids(self) -> list[ObjectId]:
        """Mock inserted_ids property."""
        return self._ids

    @property
    def deleted_count(self) -> int:
        """Mock deleted_count property."""
        return len(self._ids)


class MockCollection:
    """Mock collection class."""

    def __init__(self, *_args, **_kwargs) -> None:
        """Initialisation method."""

    def insert_many(self, documents: list[dict], ordered: bool = False):
        """Mock insert_many method."""
        return MockResult(len(documents))

    def delete_many(self, parameters: dict[str, any]):
        """Mock delete_many method."""
        return MockResult(5)

    def delete_one(self, parameters: dict[str, any]):
        """Mock delete_one method."""
        return MockResult(1)

    def update_many(self, filter: dict[str, any], update: dict[str, any], upsert: bool = False):  # noqa: A002
        """Mock update_many method."""
        return MockResult(5)

    def update_one(self, filter: dict[str, any], update: dict[str, any], upsert: bool = False):  # noqa: A002
        """Mock update_one method."""
        return MockResult(1)

    def find(
        self,
        params: dict[str, any],
        limit: int = 1000,
        projection: dict[str, any] | None = None,
        skip: int = 0,
        sort: list[tuple] | None = None,
    ):
        """Mock find method."""
        return ({"key": f"value{x}"} for x in range(5))


class UserPointsMock:
    """Mock UserPoints class."""

    def get_all_users_for_guild(self, guild_id: int) -> list[UserDB]:
        """Mocks getting all users."""
        return [
            UserDB(
                _id=ObjectId(),
                king=False,
                uid=random.randint(0, guild_id),
                guild_id=guild_id,
                name="some_name",
                points=random.randint(0, 5000),
                inactive=random.random() < 0.25,
                high_score=random.randint(500, 10000),
            )
            for _ in range(20)
        ]

    def find_user(self, user_id: int, guild_id: int) -> UserDB:
        """Find user mock."""
        return UserDB(
            _id=ObjectId(),
            king=False,
            uid=user_id,
            guild_id=guild_id,
            name=str(user_id),
            points=random.randint(10, 4567),
            daily_eddies=user_id % 2 == 0,
        )


class GuildsMock:
    """Mock Guilds class."""

    def get_guild(self, guild_id: int) -> GuildDB:
        """Mock for get_guild."""
        return GuildDB(_id=ObjectId(), guild_id=guild_id, king=3, admins=[], owner_id=guild_id, name="somename")
