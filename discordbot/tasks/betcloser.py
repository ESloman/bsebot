"""Task for closing bets."""

import asyncio
import contextlib
import dataclasses
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses.close import CloseBet
from discordbot.slashcommandeventclasses.place import PlaceBet
from discordbot.tasks.basetask import BaseTask
from discordbot.views.bet import BetView


class BetCloser(BaseTask):
    """Class for bet closer."""

    def __init__(  # noqa: PLR0913
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        place: PlaceBet,
        close: CloseBet,
    ) -> None:
        """Initialisation method.

        Args:
            bot (BSEBot): the BSEBot client
            guild_ids (list[int]): the list of guild IDs
            logger (Logger, optional): the logger to use. Defaults to PlaceHolderLogger.
            startup_tasks (list | None, optional): the list of startup tasks. Defaults to None.
            on_ready (OnReadyEvent): on ready event
            github_api (GitHubAPI): the authenticated Github api class
            place (PlaceBet): the place bet class
            close (CloseBet): the close bet class
        """
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.bet_closer

        self.embed_manager = EmbedManager(self.logger)
        self.task.start()

        self.place = place
        self.close = close

    @tasks.loop(seconds=10.0)
    async def bet_closer(self) -> None:
        """Loop that takes all our active bets and ensures they haven't expired.

        If they have expired - they get closed.
        """
        now = datetime.datetime.now()
        for guild in self.bot.guilds:
            guild_obj = await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild.id)
            for bet in active:
                if timeout := bet.timeout:
                    if timeout > now:
                        continue
                    # set the bet to no longer active ??
                    self.user_bets.update({"_id": bet._id}, {"$set": {"active": False}})  # noqa: SLF001
                    member = guild_obj.get_member(bet.user)
                    channel = await self.bot.fetch_channel(bet.channel_id)
                    message = await channel.fetch_message(bet.message_id)
                    # create a new bet with active set to False to pass around
                    _bet = dataclasses.replace(bet, active=False)

                    embed = self.embed_manager.get_bet_embed(guild_obj, bet)
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
