"""Contains our OnVoiceStateChange class.

Handles on_voice_state_change events.
"""

import dataclasses
import datetime
from zoneinfo import ZoneInfo

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnVoiceStateChange(BaseEvent):
    """Class for handling on_thread_update event."""

    def __init__(self, client: BSEBot, guild_ids: list[int]) -> None:
        """Initialisation method.

        Args:
            client (BSEBot): the connected BSEBot client
            guild_ids (list): list of supported guild IDs
        """
        super().__init__(client, guild_ids)

    def _handle_mute_status(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, vc_doc: dict[str, any]
    ) -> dict[str, str] | None:
        """Handles mute status.

        Updates the document if the mute status has changed.

        Args:
            member (discord.Member): the discord user
            before (discord.VoiceState): before state
            after (discord.VoiceState): after state
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if before.self_mute == after.self_mute:
            return None

        self.logger.info("Toggling mute status for %s in %s", member.id, after.channel.id)
        vc_doc["muted"] = after.self_mute

        if not after.self_mute:
            vc_doc["time_muted"] = (now - vc_doc["muted_time"]).total_seconds()
            vc_doc["muted_time"] = None
        else:
            vc_doc["muted_time"] = now

        return {"timestamp": now, "event": "muted" if after.self_mute else "unmuted"}

    def _handle_deaf_status(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, vc_doc: dict[str, any]
    ) -> dict[str, str] | None:
        """Handles deaf status.

        Updates the document if the deaf status has changed.

        Args:
            member (discord.Member): the discord user
            before (discord.VoiceState): before state
            after (discord.VoiceState): after state
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if before.self_deaf == after.self_deaf:
            return None

        self.logger.info("Toggling deaf status for %s in %s", member.id, after.channel.id)

        vc_doc["deafened"] = after.self_deaf
        if not after.self_deaf:
            vc_doc["time_deafened"] = (now - vc_doc["deafened_time"]).total_seconds()
            vc_doc["deafened_time"] = None
        else:
            vc_doc["deafened_time"] = now

        return {"timestamp": now, "event": "deafened" if after.self_deaf else "undeafened"}

    def _handle_stream_status(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState, vc_doc: dict[str, any]
    ) -> dict[str, str] | None:
        """Handles stream status.

        Updates the document if the stream status has changed.

        Args:
            member (discord.Member): the discord user
            before (discord.VoiceState): before state
            after (discord.VoiceState): after state
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        if before.self_stream == after.self_stream:
            return None

        self.logger.info("Toggling stream status for %s in %s", member.id, after.channel.id)
        vc_doc["streaming"] = after.self_stream

        if not after.self_stream:
            vc_doc["time_streaming"] = (now - vc_doc["streaming_time"]).total_seconds()
            vc_doc["streaming_time"] = None
        else:
            vc_doc["streaming_time"] = now

        if "vc_streaming" not in vc_doc["message_type"]:
            vc_doc["message_type"].append("vc_streaming")
        return {"timestamp": now, "event": "streaming" if after.self_stream else "unstreaming"}

    async def on_voice_state_change(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """Handles when a user changes their voice state.

        Args:
            member (discord.Member): the discord user
            before (discord.VoiceState): before state
            after (discord.VoiceState): after state
        """
        if not before.channel:
            # previous channel was None - joining a VC
            await self.joined_vc(member, after)

        if not after.channel:
            # leaving VC
            await self.left_vc(member, before)
            # don't need to handle anything else here
            return

        if before.channel and after.channel and before.channel != after.channel:
            # changing channel
            await self.left_vc(member, before)
            await self.joined_vc(member, after)

        if (
            before.self_mute != after.self_mute
            or before.self_deaf != after.self_deaf
            or before.self_stream != after.self_stream
        ):
            # mute status changed
            await self.toggle_statuses(member, before, after)

    async def joined_vc(self, member: discord.Member, after: discord.VoiceState) -> None:
        """Adds an entry into the DB when a user joins a VC.

        Args:
            member (discord.Member): the member object
            after (discord.VoiceState): voice state object
        """
        self.logger.info("User %s, %s is joining %s", member.id, member.name, after.channel)

        self.interactions.add_voice_state_entry(
            after.channel.guild.id,
            member.id,
            after.channel.id,
            datetime.datetime.now(tz=ZoneInfo("UTC")),
            after.self_mute,
            after.self_deaf,
            after.self_stream,
        )

    async def left_vc(self, member: discord.Member, before: discord.VoiceState) -> None:
        """Updates the DB entry when a user leaves.

        Args:
            member (discord.Member): the member object
            before (discord.VoiceState): voice state object
        """
        self.logger.info("User %s, %s is leaving %s", member.id, member.name, before.channel)

        now = datetime.datetime.now(tz=ZoneInfo("UTC"))

        vc_doc_db = self.interactions.find_active_voice_state(
            before.channel.guild.id, member.id, before.channel.id, now
        )

        if not vc_doc_db:
            self.logger.info("Couldn't find VC doc for %s, %s", member, before)
            return

        vc_doc = dataclasses.asdict(vc_doc_db)

        vc_doc["active"] = False
        vc_doc["left"] = now
        vc_doc["time_in_vc"] += (now - vc_doc["timestamp"]).total_seconds()

        if before.self_mute:
            vc_doc["time_muted"] += (now - vc_doc["muted_time"]).total_seconds()

        if before.self_deaf:
            vc_doc["time_deafened"] += (now - vc_doc["deafened_time"]).total_seconds()

        if before.self_stream:
            vc_doc["time_streaming"] += (now - vc_doc["streaming_time"]).total_seconds()

        event = {"timestamp": now, "event": "left"}

        self.interactions.update(
            {"_id": vc_doc["_id"]},
            {
                "$set": {
                    "active": vc_doc["active"],
                    "left": vc_doc["left"],
                    "time_in_vc": vc_doc["time_in_vc"],
                    "time_muted": vc_doc["time_muted"],
                    "time_deafened": vc_doc["time_deafened"],
                    "time_streaming": vc_doc["time_streaming"],
                },
                "$push": {"events": event},
            },
        )

    async def toggle_statuses(
        self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
    ) -> None:
        """Toggles the mute/deafened/streaming statuses for a VC interaction.

        Args:
            member (discord.Member): member object
            before (discord.VoiceState): voice state object
            after (discord.VoiceState): voice state object
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        vc_doc_db = self.interactions.find_active_voice_state(
            before.channel.guild.id, member.id, before.channel.id, now
        )

        vc_doc = dataclasses.asdict(vc_doc_db)

        new_events = [
            event
            for event in [
                getattr(self, attr)(member, before, after, vc_doc)
                for attr in ("_handle_mute_status", "_handle_deaf_status", "_handle_stream_status")
            ]
            if event
        ]

        self.interactions.update(
            {"_id": vc_doc["_id"]},
            {
                "$set": {
                    "muted": vc_doc["muted"],
                    "time_muted": vc_doc["time_muted"],
                    "muted_time": vc_doc["muted_time"],
                    "deafened": vc_doc["deafened"],
                    "time_deafened": vc_doc["time_deafened"],
                    "deafened_time": vc_doc["deafened_time"],
                    "streaming": vc_doc["streaming"],
                    "time_streaming": vc_doc["time_streaming"],
                    "streaming_time": vc_doc["streaming_time"],
                    "message_type": vc_doc["message_type"],
                },
                "$push": {"events": {"$each": new_events}},
            },
        )
