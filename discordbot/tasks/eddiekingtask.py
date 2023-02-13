import datetime

import discord
from discord.ext import tasks, commands

from discordbot.bot_enums import ActivityTypes
from mongo.bsepoints import Guilds, UserPoints
from mongo.bseticketedevents import RevolutionEvent


class BSEddiesKingTask(commands.Cog):
    def __init__(self, bot: discord.Client, guilds, logger, startup_tasks):
        self.bot = bot
        self.user_points = UserPoints()
        self.logger = logger
        self.startup_tasks = startup_tasks
        self.guilds = Guilds()
        self.events = RevolutionEvent()
        self.king_checker.start()
        self.event = None

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.king_checker.cancel()

    def _check_start_up_tasks(self) -> bool:
        """
        Checks start up tasks
        """
        for task in self.startup_tasks:
            if not task.finished:
                return False
        return True

    @tasks.loop(minutes=1)
    async def king_checker(self):
        """
        Loop that makes sure the King is assigned correctly
        :return:
        """
        if not self._check_start_up_tasks():
            self.logger.info("Startup tasks not complete - skipping loop")
            return

        for guild in self.bot.guilds:

            if events := self.events.get_open_events(guild.id):
                # ongoing revolution event - not changing the King now
                self.event = events[0]
                continue
            elif self.event is not None:
                # there was a recent event
                now = datetime.datetime.now()
                expiry_time = self.event["expired"]  # type: datetime.datetime
                if (now - expiry_time).total_seconds() < 60:
                    # only been two minutes since the event - wait
                    self.logger.info(f"The recent event {self.event} only finished {expiry_time} - waiting...")
                    continue
                self.event = None

            guild_db = self.guilds.get_guild(guild.id)
            guild = await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            # members = await guild.fetch_members()
            member_ids = [member.id for member in await guild.fetch_members().flatten()]

            role_id = guild_db.get("role")

            role = guild.get_role(role_id)  # type: discord.Role
            current_king = guild_db.get("king")
            prev_king_id = None
            if len(role.members) > 1:
                self.logger.info("We have multiple people with this role - purging the list.")
                for member in role.members:  # type: discord.Member
                    if member.id != current_king:
                        await member.remove_roles(
                            role,
                            reason="User assigned themself this role and they are NOT king."
                        )

            users = self.user_points.get_all_users_for_guild(guild.id)
            users = [u for u in users if not u.get("inactive") and u["uid"] in member_ids]
            top_user = sorted(users, key=lambda x: x["points"], reverse=True)[0]

            if current_king is not None and top_user["uid"] == current_king:
                # current king is fine
                continue

            new = guild.get_member(top_user["uid"])  # type: discord.Member
            supporter_role = await guild.get_role(guild_db["supporter_role"])  # type: discord.Role
            revo_role = await guild.get_role(guild_db["revolutionary_role"])  # type: discord.Role

            # remove KING from current user
            if current_king is not None and top_user["uid"] != current_king:
                prev_king_id = current_king
                current = guild.get_member(current_king)  # type: discord.Member
                self.logger.info(f"Removing a king: {current.display_name}")

                await current.remove_roles(role, reason="User is not longer King!")

                self.user_points.set_king_flag(current_king, guild.id, False)

                message = (f"You have been **DETHRONED** - {new.display_name} is now the "
                           f"KING of {guild.name}! :crown:")

                try:
                    await current.send(content=message)
                except discord.Forbidden:
                    pass

                activity = {
                    "type": ActivityTypes.KING_LOSS,
                    "timestamp": datetime.datetime.now(),
                    "comment": f"Losing King to {top_user['uid']}"
                }

                self.user_points.append_to_activity_history(current_king, guild.id, activity)
                current_king = None

            # make a new KING
            if current_king is None:
                self.logger.info(f"Adding a new king: {new.display_name}")

                activity = {
                    "type": ActivityTypes.KING_GAIN,
                    "timestamp": datetime.datetime.now(),
                    "comment": f"Taking King from {prev_king_id}"
                }

                self.user_points.append_to_activity_history(top_user['uid'], guild.id, activity)
                await new.add_roles(role, reason="User is now KING!")

                self.user_points.set_king_flag(top_user["uid"], guild.id, True)
                self.guilds.set_king(guild.id, top_user["uid"])

                message = f"@silent You are now the KING of {guild.name}! :crown:"
                try:
                    await new.send(content=message)
                except discord.Forbidden:
                    pass

                # everyone who was a supporter needs to lose their role now
                self.guilds.reset_pledges(guild.id)
                for member in supporter_role.members:
                    await member.remove_roles(supporter_role)
                for member in revo_role.members:
                    await member.remove_roles(revo_role)

                channel_id = guild_db.get("channel")
                if not channel_id:
                    continue

                channel = guild.get_channel(channel_id)
                await channel.trigger_typing()
                msg = f"{new.mention} is now the {role.mention}! 👑"
                await channel.send(content=msg)

    @king_checker.before_loop
    async def before_king_checker(self):
        """
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
