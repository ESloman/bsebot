
import asyncio
import datetime
from logging import Logger

import discord
from discord.ext import tasks

from discordbot.bsebot import BSEBot
from discordbot.embedmanager import EmbedManager
from discordbot.slashcommandeventclasses.close import BSEddiesCloseBet
from discordbot.slashcommandeventclasses.place import BSEddiesPlaceBet
from discordbot.tasks.basetask import BaseTask
from discordbot.views.bet import BetView


class BetCloser(BaseTask):
    def __init__(
        self,
        bot: BSEBot,
        guild_ids: list[int],
        logger: Logger,
        startup_tasks: list[BaseTask],
        place: BSEddiesPlaceBet,
        close: BSEddiesCloseBet
    ):
        super().__init__(bot, guild_ids, logger, startup_tasks)

        self.embed_manager = EmbedManager(self.logger)
        self.bet_closer.start()

        self.place = place
        self.close = close

    def cog_unload(self):
        """
        Method for cancelling the loop.
        :return:
        """
        self.bet_closer.cancel()

    @tasks.loop(seconds=10.0)
    async def bet_closer(self):
        """
        Loop that takes all our active bets and ensures they haven't expired.
        If they have expired - they get closed.
        :return:
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

                    content = self.embed_manager.get_bet_embed(guild_obj, bet["bet_id"], bet)
                    bet_view = BetView(bet, self.place, self.close)

                    # disable bet button
                    bet_view.children[0].disabled = True

                    await message.edit(content=content, view=bet_view)
                    msg = (f"[Your bet](<{message.jump_url}>) `{bet['bet_id']} - {bet['title']}` "
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
        Make sure that websocket is open before we starting querying via it.
        :return:
        """
        await self.bot.wait_until_ready()
        while not self._check_start_up_tasks():
            await asyncio.sleep(5)
