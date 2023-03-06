import datetime

import discord

from discordbot.bsebot import BSEBot
from discordbot.clienteventclasses.baseeventclass import BaseEvent


class OnVoiceStateChange(BaseEvent):
    """
    Class for handling on_thread_update event
    """

    def __init__(self, client: BSEBot, guild_ids, logger):
        super().__init__(client, guild_ids, logger)

    async def on_voice_state_change(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ) -> None:
        """
        Handles when a user changes their voice state

        :param before:
        :param after:
        :return:
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
            before.self_mute != after.self_mute or
            before.self_deaf != after.self_deaf or
            before.self_stream != after.self_stream
        ):
            # mute status changed
            await self.toggle_statuses(member, before, after)

    async def joined_vc(self, member: discord.Member, after: discord.VoiceState) -> None:
        """Adds an entry into the DB when a user joins a VC

        Args:
            member (discord.Member): the member object
            after (discord.VoiceState): voice state object
        """
        self.logger.info(f"User {member.id}, {member.name} is joining {after.channel}")

        self.interactions.add_voice_state_entry(
            after.channel.guild.id,
            member.id,
            after.channel.id,
            datetime.datetime.now(),
            after.self_mute,
            after.self_deaf,
            after.self_stream
        )

    async def left_vc(self, member: discord.Member, before: discord.VoiceState) -> None:
        """Updates the DB entry when a user leaves

        Args:
            member (discord.Member): the member object
            before (discord.VoiceState): voice state object
        """

        self.logger.info(f"User {member.id}, {member.name} is leaving {before.channel}")

        now = datetime.datetime.now()

        vc_doc = self.interactions.find_active_voice_state(
            before.channel.guild.id,
            member.id,
            before.channel.id,
            now
        )

        if not vc_doc:
            self.logger.info(f"Couldn't find VC doc for {member}, {before}")
            return

        vc_doc["active"] = False
        vc_doc["left"] = now
        vc_doc["time_in_vc"] += (now - vc_doc["timestamp"]).total_seconds()

        if before.self_mute:
            vc_doc["time_muted"] += (now - vc_doc["muted_time"]).total_seconds()

        if before.self_deaf:
            vc_doc["time_deafened"] += (now - vc_doc["deafened_time"]).total_seconds()

        if before.self_stream:
            vc_doc["time_streaming"] += (now - vc_doc["streaming_time"]).total_seconds()

        vc_doc["events"].append(
            {"timestamp": now, "event": "left"}
        )

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
                    "events": vc_doc["events"]
                }
            }
        )

    async def toggle_statuses(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState
    ):
        """Toggles the mute/deafened/streaming statuses for a VC interaction

        Args:
            member (discord.Member): member object
            before (discord.VoiceState): voice state object
            after (discord.VoiceState): voice state object
        """

        now = datetime.datetime.now()
        vc_doc = self.interactions.find_active_voice_state(
            before.channel.guild.id,
            member.id,
            before.channel.id,
            now
        )

        if before.self_mute != after.self_mute:
            self.logger.info(f"Toggling mute status for {member.id} in {after.channel.id}")

            vc_doc["muted"] = after.self_mute

            if not after.self_mute:
                vc_doc["time_muted"] = (now - vc_doc["muted_time"]).total_seconds()
                vc_doc["muted_time"] = None
            elif after.self_mute:
                vc_doc["muted_time"] = now

            vc_doc["events"].append(
                {"timestamp": now, "event": "muted" if after.self_mute else "unmuted"}
            )

        if before.self_deaf != after.self_deaf:

            self.logger.info(f"Toggling deaf status for {member.id} in {after.channel.id}")

            vc_doc["deafened"] = after.self_deaf

            if not after.self_deaf:
                vc_doc["time_deafened"] = (now - vc_doc["deafened_time"]).total_seconds()
                vc_doc["deafened_time"] = None
            elif after.self_deaf:
                vc_doc["deafened_time"] = now

            vc_doc["events"].append(
                {"timestamp": now, "event": "deafened" if after.self_deaf else "undeafened"}
            )

        if before.self_stream != after.self_stream:

            self.logger.info(f"Toggling stream status for {member.id} in {after.channel.id}")

            vc_doc["streaming"] = after.self_stream

            if not after.self_stream:
                vc_doc["time_streaming"] = (now - vc_doc["streaming_time"]).total_seconds()
                vc_doc["streaming_time"] = None
            elif after.self_stream:
                vc_doc["streaming_time"] = now

            vc_doc["events"].append(
                {"timestamp": now, "event": "streaming" if after.self_stream else "unstreaming"}
            )

            if "vc_streaming" not in vc_doc["message_type"]:
                vc_doc["message_type"].append("vc_streaming")

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
                    "events": vc_doc["events"],
                    "message_type": vc_doc["message_type"],
                }
            }
        )
