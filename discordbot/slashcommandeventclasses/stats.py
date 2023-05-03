
import datetime

import discord

from discordbot.bot_enums import ActivityTypes
from discordbot.constants import BSE_SERVER_ID, JERK_OFF_CHAT
from discordbot.slashcommandeventclasses.bseddies import BSEddies
from discordbot.stats.statsclasses import StatsGatherer
from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.views.wrapped import WrappedView


class Stats(BSEddies):
    """
    Class for handling `/stats` commands
    """

    def __init__(self, client, guilds, logger):
        super().__init__(client, guilds, logger)
        self.activity_type = ActivityTypes.STATS
        self.help_string = "View some stats"
        self.command_name = "stats"

    async def create_stats_view(self, ctx: discord.ApplicationContext) -> None:
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.STATS)

    async def replay(self, ctx: discord.ApplicationContext, year: int) -> None:
        """Generates a replay message and stats and sends that to the given user

        Args:
            ctx (discord.ApplicationContext): the application command context
            year (int): the year to generate the replay for
        """
        if not await self._handle_validation(ctx):
            return

        await ctx.defer(ephemeral=True)

        self._add_event_type_to_activity_history(ctx.author, ctx.guild_id, ActivityTypes.REPLAY22)

        now = datetime.datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1, year=year, month=1)
        end = start.replace(month=1, year=year + 1)

        uid = ctx.author.id
        replay_message = await self.stats(uid, start, end, ctx.guild)
        replay_message = (
            f"<@!{uid}>'s **BSEWrapped _2022_**:\n\n"
            f"{replay_message}"
        )

        wrapped_view = WrappedView()
        await ctx.followup.send(content=replay_message, view=wrapped_view, ephemeral=True)

    async def stats(
        self,
        user_id: int,
        start: datetime.datetime,
        end: datetime.datetime,
        guild: discord.Guild
    ) -> None:
        """
        Command for handling gathering stats for various Stats commands (/stats and /replayXXXX)

        :param user_id: the user ID to get stats for
        :param start: the start date for stats
        :param end: the end date for stats
        :param guild: the guild object
        :return:
        """
        stats_gatherer = StatsGatherer(self.logger, True)
        cache = StatsDataCache(uid=user_id)

        # set the gatherer's cache to one that limits to UID
        stats_gatherer.cache = cache

        args = (BSE_SERVER_ID, start, end)

        most_messages = stats_gatherer.most_messages_sent(*args)
        longest_message = stats_gatherer.longest_message(*args)
        best_wordle = stats_gatherer.lowest_average_wordle_score(*args)
        most_bets = stats_gatherer.most_bets_created(*args)
        most_eddies_placed = stats_gatherer.most_eddies_bet(*args)
        most_eddies_won = stats_gatherer.most_eddies_won(*args)
        time_king = stats_gatherer.most_time_king(*args)
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
        busiest_day = stats_gatherer.busiest_day(*args)
        most_used_emoji = stats_gatherer.most_popular_server_emoji(*args, user_id)

        _chan = sorted(
            diverse_portfolio.users[user_id]["channels"],
            key=lambda x: diverse_portfolio.users[user_id]["channels"][x], reverse=True
        )[0]
        _least_fav_chan = sorted(
            diverse_portfolio.users[user_id]["channels"],
            key=lambda x: diverse_portfolio.users[user_id]["channels"][x], reverse=True
        )[-1]
        _perc = (diverse_portfolio.users[user_id]["channels"][_chan] / most_messages.value) * 100
        _lf_perc = (diverse_portfolio.users[user_id]["channels"][_least_fav_chan] / most_messages.value) * 100

        _vc_time = int(big_gamer.users.get(user_id, {"count": 0})["count"])
        _king_time = int(time_king.kings.get(user_id, 0))
        _streaming_time = int(big_streamer.users.get(user_id, {"count": 0})["count"])
        _dv_num = diverse_portfolio.users.get(user_id, {"channels": {_chan: 0}})["channels"][_chan]
        _lv_num = diverse_portfolio.users.get(user_id, {"channels": {_least_fav_chan: 0}})["channels"][_least_fav_chan]

        try:
            lft = await self.client.fetch_channel(_least_fav_chan)
            if lft.archived:
                _least_fav_text = f"`#{lft.name} (archived)`"
            else:
                _least_fav_text = f"<#{_least_fav_chan}>"
        except Exception:
            _least_fav_text = f"<#{_least_fav_chan}>"

        busiest_day_format = busiest_day.value.strftime("%a %d %b")

        try:
            emoji_obj = await guild.fetch_emoji(most_used_emoji.emoji_id)
        except Exception:
            emoji_obj = most_used_emoji.emoji_id

        message = (
            f"Messages sent: `{most_messages.value}` "
            f"(in _{len(most_messages.message_users[user_id]['channels'])}_ channels and "
            f"_{len(most_messages.message_users[user_id]['threads'])}_ threads)\n"

            f"Number of channels and threads participated in: `{diverse_portfolio.value}`\n"

            f"Favourite channel: <#{_chan}> (**{f'{round(_perc, 2)}%'}** of messages (`{_dv_num}`) sent)\n"

            f"Least favourite channel: {_least_fav_text} "
            f"(**{f'{round(_lf_perc, 2)}%'}** of messages (`{_lv_num}`) sent)\n"

            f"Your longest message: `{longest_message.value}`\n"

            f"Busiest day: `{busiest_day_format}` "
            f"(**{busiest_day.messages}** messages in _{busiest_day.channels}_ channels)\n"

            f"Your wordle average: `{best_wordle.value}`\n"

            f"Number of twitter links shared: `{twitter_addict.value}`\n"

            f"Number of contributions to <#{JERK_OFF_CHAT}>: `{jerk_off_king.value}`\n"

            f"Reactions received: `{big_memer.reactees.get(user_id, 0)}`\n"

            f"Reactions given: `{react_king.reaction_users.get(user_id, 0)}`\n"

            f"Replies received: `{conversation_starter.repliees.get(user_id, 0)}`\n"

            f"Replies given: `{serial_replier.repliers.get(user_id, 0)}`\n"

            f"Number of edits: `{fattest_fingers.value}`\n"

            f"Number of swears: `{most_swears.value}`\n"

            f"Your favourite server emoji: {emoji_obj} (`{most_used_emoji.count}`)\n"

            f"Time spent in VCs: `{str(datetime.timedelta(seconds=_vc_time))}`\n"

            f"Time spent streaming: `{str(datetime.timedelta(seconds=_streaming_time))}`\n"

            f"Time spent king: `{str(datetime.timedelta(seconds=_king_time))}`\n"

            f"Bets created: `{most_bets.bookies.get(user_id, 0)}`\n"

            f"Eddies placed on bets: `{most_eddies_placed.betters.get(user_id, 0)}`\n"

            f"Eddies won: `{most_eddies_won.bet_winners.get(user_id, 0)}`"
        )

        return message
