"""Contains our OnEmojiCreate class.

Handles on_emoji_create events.
"""

import datetime
from zoneinfo import ZoneInfo

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnEmojiCreate(BaseEvent):
    """Class for handling OnEmojiCreate events."""

    def __init__(self, client: BSEBot) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
        """
        super().__init__(client)

    async def on_emojis_update(self, guild_id: int, _: list[discord.Emoji], after: list[discord.Emoji]) -> None:
        """Handling on emoji creation events.

        Args:
            guild_id (int): the guild ID the event is happening in
            _ (list[discord.Emoji]): the list of emojis before
            after (list[discord.Emoji]): the list of emojis after
        """
        guild = await self.client.fetch_guild(guild_id)

        for emoji in after:
            if _ := self.server_emojis.get_emoji(guild_id, emoji.id):
                # do something here to make sure nothing has changed
                continue

            new_emoji_obj = await guild.fetch_emoji(emoji.id)

            self.logger.info("New emoji, %s, created!", emoji.name)
            self.server_emojis.insert_emoji(emoji.id, emoji.name, emoji.created_at, new_emoji_obj.user.id, guild_id)

            self.interactions.add_entry(
                emoji.id,
                guild_id,
                new_emoji_obj.user.id,
                guild_id,
                [
                    "emoji_created",
                ],
                emoji.name,
                datetime.datetime.now(tz=ZoneInfo("UTC")),
                additional_keys={"emoji_id": emoji.id, "created_at": emoji.created_at},
            )
