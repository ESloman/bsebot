"""Contains our BSEBot class.

Class exists to override fetch_guild and fetch_channel to make less API calls.
"""

import discord
from slomanlogger import SlomanLogger


class BSEBot(discord.Bot):
    """BSEBot class.

    Inherits from discord.Bot. Re-implements the fetch_guild and fetch_channel methods to make less API calls.
    """

    def __init__(
        self: "BSEBot",
        intents: discord.Intents,
        activity: discord.Activity,
        max_messages: int = 5000,
    ) -> None:
        """Our own implementation of discord.Bot.

        Allows us to override some methods to better suit our needs and be a bit more efficient.

        Args:
            intents (discord.Intents): _description_
            activity (discord.Activity): _description_
            max_messages (int, optional): _description_. Defaults to 5000.
        """
        super().__init__(intents=intents, activity=activity, auto_sync_commands=True, max_messages=max_messages)
        self.logger = SlomanLogger("bsebot")

    async def fetch_guild(self: "BSEBot", guild_id: int, /) -> discord.Guild | None:
        """Wrapper for getting guild and using an API call if cache is empty.

        Args:
            guild_id (int): the guild ID to fetch

        Returns:
            discord.Guild
        """
        guild = super().get_guild(guild_id)
        if not guild:
            self.logger.debug("Couldn't get guild %s, fetching instead", guild_id)
            guild = await super().fetch_guild(guild_id)
        return guild

    async def fetch_channel(
        self: "BSEBot",
        channel_id: int,
        /,
    ) -> discord.abc.GuildChannel | discord.Thread | discord.abc.PrivateChannel | None:
        """Wrapper for getting channel and using an API call if cache is empty.

        Args:
            channel_id (int): the channel ID to fetch

        Returns:
            discord.GuildChannel | discord.Thread | discord.PrivateChannel | None: _description_
        """
        channel = super().get_channel(channel_id)
        if not channel:
            self.logger.debug("Couldn't get channel %s, fetching instead", channel_id)
            channel = await super().fetch_channel(channel_id)
        return channel
