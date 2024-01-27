"""BSEBot mock."""

from discordbot.constants import BSE_BOT_ID
from tests.mocks import discord_mocks


class BSEBotMock:
    @property
    def user(self) -> discord_mocks.MemberMock:
        """Mocks the user property."""
        return discord_mocks.MemberMock(BSE_BOT_ID, "BSEBot")

    async def wait_until_ready(self) -> bool:
        """Mocks wait until ready method."""
        return True

    async def fetch_guild(self, guild_id: int):
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
