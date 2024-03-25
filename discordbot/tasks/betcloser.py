"""Task for closing bets."""

import asyncio
import contextlib
import dataclasses
import datetime
from typing import TYPE_CHECKING
from zoneinfo import ZoneInfo

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.tasks.basetask import BaseTask, TaskSchedule
from discordbot.views.bet import BetView

if TYPE_CHECKING:
    from discordbot.slashcommandeventclasses.close import CloseBet
    from discordbot.slashcommandeventclasses.place import PlaceBet


class BetCloser(BaseTask):
    """Class for bet closer."""

    def __init__(
        self,
        bot: BSEBot,
        startup_tasks: list[BaseTask],
        place: "PlaceBet",
        close: "CloseBet",
        start: bool = False,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            github_api (GitHubAPI): the authenticated Github api class
            place (PlaceBet): the place bet class
            close (CloseBet): the close bet class
            start (bool) whether to start the task. Defaults to False.
        """
        super().__init__(bot, startup_tasks)
        self.schedule = TaskSchedule(range(7), range(24))
        self.task = self.bet_closer

        self.embed_manager = EmbedManager()
        self.place: "PlaceBet" = place
        self.close: "CloseBet" = close
        if start:
            self.task.start()

    @tasks.loop(seconds=15.0)
    async def bet_closer(self) -> None:
        """Loop that takes all our active bets and ensures they haven't expired.

        If they have expired - they get closed.
        """
        now = datetime.datetime.now(tz=ZoneInfo("UTC"))
        for guild in self.bot.guilds:
            guild_obj = await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild.id)
            for bet in active:
                timeout = bet.timeout
                if not timeout or timeout > now:
                    continue
                # set the bet to no longer active
                self.user_bets.update({"_id": bet._id}, {"$set": {"active": False}})  # noqa: SLF001
                member = guild_obj.get_member(bet.user)
                channel = await self.bot.fetch_channel(bet.channel_id)
                message = await channel.fetch_message(bet.message_id)
                # create a new bet with active set to False to pass around
                _bet = dataclasses.replace(bet, active=False)

                embed = self.embed_manager.get_bet_embed(bet)
                content = f"# {_bet.title}\n_Created by <@{_bet.user}>_"
                bet_view = BetView(_bet, self.place, self.close)

                # disable bet button
                bet_view.children[0].disabled = True

                await message.edit(content=content, embed=embed, view=bet_view)
                msg = (
                    f"[Your bet](<{message.jump_url}>) `{_bet.bet_id} - {_bet.title}` "
                    f"is now closed for bets and is waiting a result from you."
                )
                if not member.dm_channel:
                    await member.create_dm()
                with contextlib.suppress(discord.Forbidden):
                    await member.send(content=msg, silent=True)

    @bet_closer.before_loop
    async def before_bet_closer(self) -> None:
        """Make sure that websocket is open before we start querying via it."""
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
