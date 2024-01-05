"""Mocks for mongo classes."""

import random

from bson import ObjectId

from mongo.datatypes.datatypes import GuildDB
from mongo.datatypes.user import UserDB


class UserPointsMock:
    def get_all_users_for_guild(self, guild_id: int) -> list[UserDB]:  # noqa: PLR6301
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

    def find_user(self, user_id: int, guild_id: int) -> UserDB:  # noqa: PLR6301
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
    def get_guild(self, guild_id: int) -> GuildDB:  # noqa: PLR6301
        """Mock for get_guild."""
        return GuildDB(_id=ObjectId(), guild_id=guild_id, king=3, admins=[], owner_id=guild_id, name="somename")
