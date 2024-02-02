"""Contains our OnStickerCreate class.

Handles on_sticker_update events.
"""

import datetime
import logging

import discord
import pytz

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnStickerCreate(BaseEvent):
    """Class for handling on_sticker_update event."""

    def __init__(self, client: BSEBot, guild_ids: list, logger: logging.Logger) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
            logger (logging.Logger): the logger
        """
        super().__init__(client, guild_ids, logger)

    async def on_stickers_update(
        self,
        guild_id: int,
        _: list[discord.GuildSticker],
        after: list[discord.GuildSticker],
    ) -> None:
        """Handles on_stickers_update events.

        Args:
            guild_id (int): the guild id
            _ (list[discord.GuildSticker]): the list of stickers before the update
            after (list[discord.GuildSticker]): the list of stickers after the update
        """
        guild = await self.client.fetch_guild(guild_id)

        for sticker in after:
            if _ := self.server_stickers.get_sticker(guild_id, sticker.id):
                # do something here to make sure nothing has changed
                continue

            new_stick_obj = await guild.fetch_sticker(sticker.id)

            self.logger.info("New sticker, %s, created!", new_stick_obj.name)
            self.server_stickers.insert_sticker(
                sticker.id,
                sticker.name,
                sticker.created_at,
                new_stick_obj.user.id,
                guild_id,
            )

            self.interactions.add_entry(
                sticker.id,
                guild_id,
                new_stick_obj.user.id,
                guild_id,
                [
                    "sticker_created",
                ],
                sticker.name,
                datetime.datetime.now(tz=pytz.utc),
                additional_keys={"sticker_id": sticker.id, "created_at": sticker.created_at},
            )
