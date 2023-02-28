
import discord


class BSEBot(discord.Bot):
    def __init__(self, intents: discord.Intents, activity: discord.Activity, max_messages: int = 5000) -> None:
        super().__init__(intents=intents, activity=activity, auto_sync_commands=True, max_messages=max_messages)

    async def fetch_guild(self, id: int, /) -> discord.Guild | None:
        """
        Wrapper for getting guild and using an API call if cache is empty

        Args:
            id (int): the guild ID to fetch

        Returns:
            discord.Guild
        """
        guild = super().get_guild(id)
        if not guild:
            guild = await super().fetch_guild(id)
        return guild

    async def fetch_channel(
        self,
        id: int,
        /
    ) -> discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None:
        """
        Wrapper for getting channel and using an API call if cache is empty

        Args:
            id (int): the channel ID to fetch

        Returns:
            discord.GuildChannel | discord.Thread | discord.PrivateChannel | None: _description_
        """
        channel = super().get_channel(id)
        if not channel:
            channel = await super().fetch_channel(id)
        return channel
