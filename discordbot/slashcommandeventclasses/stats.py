
import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSE_SERVER_ID
from discordbot.slashcommandeventclasses import BSEddies
from discordbot.stats.statsclasses import StatsGatherer
from discordbot.stats.statsdatacache import StatsDataCache


class BSEddiesStats(BSEddies):
    """
    Class for handling `/stats` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)

    async def stats(self, ctx: discord.ApplicationContext) -> None:
        """
        Basic view method for handling view slash commands.

        Sends an ephemeral message to the user with their total eddies and any "pending" eddies they
        have tied up in bets.

        :param ctx:
        :return:
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.STATS)

        now = datetime.datetime.now()

        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1, year=2022, month=1)
        if start.month == 12:
            new_month = 1
        else:
            new_month = start.month + 1
        end = start.replace(month=1, year=2023)

        stats_gatherer = StatsGatherer(self.logger, True)
        cache = StatsDataCache(uid=ctx.author.id)

        # set the gatherer's cache to one that limits to UID
        stats_gatherer.cache = cache

        args = (BSE_SERVER_ID, start, end)

        most_messages = stats_gatherer.most_messages_sent(*args)
        longest_message = stats_gatherer.longest_message(*args)
        best_wordle = stats_gatherer.lowest_average_wordle_score(*args)
        most_bets = stats_gatherer.most_bets_created(*args)
        most_eddies_placed = stats_gatherer.most_eddies_bet(*args)
        most_eddies_won = stats_gatherer.most_eddies_won(*args)
        twitter_addict = stats_gatherer.twitter_addict(*args)
        jerk_off_king = stats_gatherer.jerk_off_contributor(*args)
        big_memer = stats_gatherer.big_memer(*args)
        react_king = stats_gatherer.react_king(*args)
        big_gamer = stats_gatherer.big_gamer(*args)
        big_streamer = stats_gatherer.big_streamer(*args)
        serial_replier, conversation_starter = stats_gatherer.most_replies(*args)
        fattest_fingers = stats_gatherer.most_edited_messages(*args)
        most_swears = stats_gatherer.most_swears(*args)
        diverse_portfolio = stats_gatherer.most_messages_to_most_channels(*args)

        message = (
            f"Messages sent: `{most_messages.value}`\n"
            f"Your longest message: `{longest_message.value}`\n"
            f"Your wordle average: `{best_wordle.value}`\n"
            f"Number of twitter links shared: `{twitter_addict.value}`\n"
            f"Number of jerk-off-chat contribs: `{jerk_off_king.value}`\n"
            f"Reactions received: `{big_memer.reactees[ctx.author.id]}`\n"
            f"Reactions given: `{react_king.reaction_users[ctx.author.id]}`\n"
            f"Replies received: `{conversation_starter.repliees[ctx.author.id]}`\n"
            f"Replies given: `{serial_replier.repliers[ctx.author.id]}`\n"
            f"Number of edits: `{fattest_fingers.value}`\n"
            f"Number of swears: `{most_swears.value}`\n"
            f"Number of channels: `{diverse_portfolio.value}`\n"
        )

        await ctx.followup.send(content=message, ephemeral=True)
