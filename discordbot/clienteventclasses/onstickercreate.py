import datetime
from typing import List

import discord

from discordbot.baseeventclass import BaseEvent
from mongo.bsepoints import UserInteractions


class OnStickerCreate(BaseEvent):
    def __init__(self, client: discord.Bot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)
        self.user_interactions = UserInteractions()

    async def on_stickers_update(
            self,
            guild_id: int,
            before: List[discord.GuildSticker],
            after: List[discord.GuildSticker]
    ) -> None:

        guild = await self.client.fetch_guild(guild_id)

        for sticker in after:
            if stick_obj := self.server_stickers.get_sticker(guild_id, sticker.id):
                # do something here to make sure nothing has changed
                continue

            new_stick_obj = await guild.fetch_sticker(sticker.id)

            self.logger.info(f"New sticker, {stick_obj.name}, created!")
            self.server_stickers.insert_sticker(
                sticker.id,
                sticker.name,
                sticker.created_at,
                new_stick_obj.user.id,
                guild_id
            )

            self.user_interactions.add_entry(
                sticker.id,
                guild_id,
                new_stick_obj.user.id,
                guild_id,
                ["sticker_created", ],
                sticker.name,
                datetime.datetime.now(),
                {"sticker_id": sticker.id, "created_at": sticker.created_at}
            )
