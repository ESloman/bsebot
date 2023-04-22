
import asyncio
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
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        place: PlaceBet,
        close: CloseBet
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)
        self.task = self.bet_closer

        self.embed_manager = EmbedManager(self.logger)
        self.task.start()

        self.place = place
        self.close = close

    @tasks.loop(seconds=10.0)
    async def bet_closer(self):
        """
        Loop that takes all our active bets and ensures they haven't expired.
        If they have expired - they get closed.
        """

        now = datetime.datetime.now()
        for guild in self.bot.guilds:
            guild_obj = await self.bot.fetch_guild(guild.id)  # type: discord.Guild
            active = self.user_bets.get_all_active_bets(guild.id)
            for bet in active:
                if timeout := bet.get("timeout"):
                    if timeout > now:
                        continue
                    # set the bet to no longer active ??
                    self.user_bets.update({"_id": bet["_id"]}, {"$set": {"active": False}})
                    member = guild_obj.get_member(bet["user"])
                    channel = await self.bot.fetch_channel(bet["channel_id"])
                    message = await channel.fetch_message(bet["message_id"])  # type: discord.Message
                    bet["active"] = False

                    embed = self.embed_manager.get_bet_embed(guild_obj, bet["bet_id"], bet)
                    bet_view = BetView(bet, self.place, self.close)

                    # disable bet button
                    bet_view.children[0].disabled = True

                    await message.edit(embed=embed, view=bet_view)
                    msg = (f"Your bet `{bet['bet_id']} - {bet['title']}` (<{message.jump_url}>) "
                           f"is now closed for bets and is waiting a result from you.")
                    if not member.dm_channel:
                        await member.create_dm()
                    try:
                        await member.send(content=msg, silent=True)
                    except discord.Forbidden:
                        pass

    @bet_closer.before_loop
    async def before_bet_closer(self):
        """
        Make sure that websocket is open before we start querying via it.
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
