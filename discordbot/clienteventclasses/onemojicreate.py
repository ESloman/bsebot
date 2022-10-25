import datetime
from typing import List

import discord

from discordbot.baseeventclass import BaseEvent
from mongo.bsepoints import UserInteractions


class OnEmojiCreate(BaseEvent):
    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.user_interactions = UserInteractions()

    async def on_emojis_update(self, guild_id: int, before: List[discord.Emoji], after: List[discord.Emoji]) -> None:

        guild = await self.client.fetch_guild(guild_id)
        
        for emoji in after:
            if emoji_obj := self.server_emojis.get_emoji(guild_id, emoji.id):
                # do something here to make sure nothing has changed
                continue
            
            new_emoji_obj = await guild.fetch_emoji(emoji.id)

            self.logger.info(f"New emoji, {emoji.name}, created!")
            self.server_emojis.insert_emoji(
                emoji.id,
                emoji.name,
                emoji.created_at,
                new_emoji_obj.user.id,
                guild_id
            )

            self.user_interactions.add_entry(
                emoji.id,
                guild_id,
                new_emoji_obj.user.id,
                guild_id,
                ["emoji_created", ],
                emoji.name,
                datetime.datetime.now(),
                {"emoji_id": emoji.id, "created_at": emoji.created_at}
            )
