"""BSEBot mock."""

from tests.mocks import discord_mocks


class BSEBotMock:
    async def wait_until_ready(self) -> bool:  # noqa: PLR6301
        """Mocks wait until ready method."""
        return True

    async def fetch_guild(self, guild_id: int):  # noqa: PLR6301
        """Mock for fetch guild."""
        return discord_mocks.GuildMock(guild_id)


def get_guild(self: any, guild_id: int) -> discord_mocks.GuildMock:
    """Get guild mock."""
    if guild_id == 456:
        return None
    return discord_mocks.GuildMock(guild_id)


async def fetch_guild(self: any, guild_id: int) -> discord_mocks.GuildMock:
    """Fetch guild mock."""
    return discord_mocks.GuildMock(guild_id)


def get_channel(self: any, channel_id: int) -> discord_mocks.ChannelMock:
    """Get channel mock."""
    if channel_id == 654321:
        return None
    return discord_mocks.ChannelMock(channel_id)


async def fetch_channel(self: any, channel_id: int) -> discord_mocks.ChannelMock:
    """Fetch channel mock."""
    return discord_mocks.ChannelMock(channel_id)