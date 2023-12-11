"""BSEBot mock."""

from tests.mocks import discord_mocks


class BSEBotMock:
    async def wait_until_ready(self) -> bool:  # noqa: PLR6301
        """Mocks wait until ready method."""
        return True

    async def fetch_guild(self, guild_id: int):  # noqa: PLR6301
        """Mock for fetch guild."""
        return discord_mocks.GuildMock(guild_id)
