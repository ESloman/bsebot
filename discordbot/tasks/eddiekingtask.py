"""Task for setting the King."""

import asyncio
import contextlib
import datetime
from logging import Logger
from typing import TYPE_CHECKING

import discord
import pytz
from discord.ext import tasks

from discordbot.bot_enums import ActivityTypes
from discordbot.bsebot import BSEBot
from discordbot.tasks.basetask import BaseTask

if TYPE_CHECKING:
    from mongo.datatypes.revolution import RevolutionEventDB


class BSEddiesKingTask(BaseTask):
    """Class for BSEddies King task."""

    def __init__(self, bot: BSEBot, guild_ids: list[int], logger: Logger, startup_tasks: list[BaseTask]) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.king_checker
        self.task.start()
        self.events_cache: dict[int, RevolutionEventDB] = {}

    @tasks.loop(minutes=1)
    async def king_checker(self) -> None:  # noqa: C901, PLR0912, PLR0915
        """Loop that makes sure the King is assigned correctly."""
        for _guild in self.bot.guilds:
            if events := self.revolutions.get_open_events(_guild.id):
                # ongoing revolution event - not changing the King now
                self.events_cache[_guild.id] = events[0]
                continue

            if event := self.events_cache.get(_guild.id):
                # there was a recent event
                now = datetime.datetime.now(tz=pytz.utc)
                expiry_time = event.expired  # type: datetime.datetime
                if (now - expiry_time).total_seconds() < 60:  # noqa: PLR2004
                    # only been two minutes since the event - wait
                    self.logger.info("The recent event %s only finished %s - waiting...", event, expiry_time)
                    continue
                self.events_cache[_guild.id] = None

            guild_db = self.guilds.get_guild(_guild.id)
            guild = await self.bot.fetch_guild(_guild.id)  # type: discord.Guild
            member_ids = [member.id for member in await guild.fetch_members().flatten()]

            role_id = guild_db.role

            role = guild.get_role(role_id)  # type: discord.Role
            current_king = guild_db.king
            prev_king_id = None

            if not role and not role_id:
                self.logger.warning(
                    "No BSEddies role defined for %s: %s. Can't check KING so skipping.", guild.id, guild.name
                )
                continue

            if len(role.members) > 1:
                self.logger.info("We have multiple people with this role - purging the list.")
                for member in role.members:  # type: discord.Member
                    if member.id != current_king:
                        await member.remove_roles(
                            role,
                            reason="User assigned themself this role and they are NOT king.",
                        )

            users = self.user_points.get_all_users_for_guild(guild.id)
            users = [u for u in users if not u.inactive and u.uid in member_ids]
            top_user = sorted(users, key=lambda x: x.points, reverse=True)[0]

            if current_king is not None and top_user.uid == current_king:
                # current king is fine
                continue

            new = guild.get_member(top_user.uid)  # type: discord.Member
            if not new:
                new = await guild.fetch_member(top_user.uid)

            supporter_role = guild.get_role(guild_db.supporter_role)  # type: discord.Role
            revo_role = guild.get_role(guild_db.revolutionary_role)  # type: discord.Role

            # remove KING from current user
            if current_king is not None and top_user.uid != current_king:
                prev_king_id = current_king

                current = guild.get_member(current_king)
                if not current:
                    current = await guild.fetch_member(current_king)  # type: discord.Member

                self.logger.info("Removing a king: %s", current.display_name)

                await current.remove_roles(role, reason="User is not longer King!")

                self.user_points.set_king_flag(current_king, guild.id, False)

                message = f"You have been **DETHRONED** - {new.display_name} is now the KING of {guild.name}! :crown:"

                with contextlib.suppress(discord.Forbidden):
                    await current.send(content=message, silent=True)

                self.activities.add_activity(
                    current_king,
                    guild.id,
                    ActivityTypes.KING_LOSS,
                    comment=f"Losing King to {top_user.uid}",
                )
                current_king = None

                # rename role names
                if supporter_role.name != "Supporters":
                    await supporter_role.edit(name="Supporters")
                if revo_role.name != "Revolutionaries":
                    await revo_role.edit(name="Revolutionaries")

            # make a new KING
            if current_king is None:
                self.logger.info("Adding a new king: %s", new.display_name)

                self.activities.add_activity(
                    top_user.uid,
                    guild.id,
                    ActivityTypes.KING_GAIN,
                    comment=f"Taking King from {prev_king_id}",
                )

                await new.add_roles(role, reason="User is now KING!")

                self.user_points.set_king_flag(top_user.uid, guild.id, True)
                self.guilds.set_king(guild.id, top_user.uid)

                message = f"You are now the KING of {guild.name}! :crown:"
                with contextlib.suppress(discord.Forbidden):
                    await new.send(content=message, silent=True)

                # everyone who was a supporter needs to lose their role now
                self.guilds.reset_pledges(guild.id)
                for member in supporter_role.members:
                    await member.remove_roles(supporter_role)
                for member in revo_role.members:
                    await member.remove_roles(revo_role)

                channel_id = guild_db.channel
                if not channel_id:
                    continue

                channel = await self.bot.fetch_channel(channel_id)
                await channel.trigger_typing()
                msg = f"{new.mention} is now the {role.mention}! 👑"
                await channel.send(content=msg)

    @king_checker.before_loop
    async def before_king_checker(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
