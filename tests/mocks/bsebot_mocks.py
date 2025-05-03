"""BSEBot mock."""

import discord

from discordbot.constants import BSE_BOT_ID
from tests.mocks import discord_mocks


class BSEBotMock:
    def __init__(self) -> None:
        """Initialisation method."""
        self._guilds = [
            {"guild_id": "g1234567", "owner_id": "o1234567", "name": "name"},
            {"guild_id": "g123456789", "owner_id": "o123456789", "name": "name123"},
        ]

    @property
    def user(self) -> discord_mocks.MemberMock:
        """Mocks the user property."""
        return discord_mocks.MemberMock(BSE_BOT_ID, "BSEBot")

    @property
    def guilds(self):
        """Mock for guilds property."""
        return [discord_mocks.GuildMock(guild["guild_id"], guild["owner_id"], guild["name"]) for guild in self._guilds]

    def add_view(self, *args, **kwargs) -> None:
        """Mock for adding a view."""

    async def wait_until_ready(self) -> bool:
        """Mocks wait until ready method."""
        return True

    async def fetch_user(self, user_id: int):
        """Mock for fetch user."""
        return discord_mocks.MemberMock(user_id)

    async def fetch_guild(self, guild_id: int):
        """Mock for fetch guild."""
        return discord_mocks.GuildMock(guild_id)

    async def fetch_channel(self, channel_id: int):
        """Mock for fetch guild."""
        return discord_mocks.ChannelMock(channel_id)

    async def change_presence(self, activity: discord.Activity) -> None:
        """Mock for changing presence."""

    async def fetch_guilds(self):
        """Mock for fetching guilds."""
        for guild in self._guilds:
            yield discord_mocks.GuildMock(guild["guild_id"], guild["owner_id"], guild["name"])


def get_guild(self: any, guild_id: int) -> discord_mocks.GuildMock:
    """Get guild mock."""
    if guild_id == 456:
        return None
    return discord_mocks.GuildMock(guild_id)


async def fetch_guild(self: any, guild_id: int) -> discord_mocks.GuildMock:  # noqa: RUF029
    """Fetch guild mock."""
    return discord_mocks.GuildMock(guild_id)


def get_channel(self: any, channel_id: int) -> discord_mocks.ChannelMock:
    """Get channel mock."""
    if channel_id == 654321:
        return None
    return discord_mocks.ChannelMock(channel_id)


async def fetch_channel(self: any, channel_id: int) -> discord_mocks.ChannelMock:  # noqa: RUF029
    """Fetch channel mock."""
    return discord_mocks.ChannelMock(channel_id)
