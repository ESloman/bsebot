import datetime
from typing import Tuple

import discord

from discordbot.stats.statsdatacache import StatsDataCache
from mongo.bsedataclasses import Awards
from mongo.bsepoints import UserPoints


class PersonalStatsBuilder:
    def __init__(self, bot: discord.Client, logger):
        self.bot = bot
        self.logger = logger
        self.cache = StatsDataCache()

    @staticmethod
    def get_monthly_datetime_objects() -> Tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous month

        Returns:
            Tuple[datetime.datetime, datetime.datetime]:
        """
        now = datetime.datetime.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=1)

        if start.month == 12:
            new_month = 1
        else:
            new_month = start.month + 1

        end = start.replace(month=new_month)
        return start, end

    @staticmethod
    def get_annual_datetime_objects() -> Tuple[datetime.datetime, datetime.datetime]:
        """Returns two datetime objects that sandwich the previous year

        Returns:
            Tuple[datetime.datetime, datetime.datetime]:
        """
        now = datetime.datetime.now()

        # always create so it's the first of the month of the current year
        end = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=1)
        # always be the first of the previous year
        start = end.replace(year=end.year - 1)

        return start, end

    async def get_stats_message_for_user(
        self,
        guild_id: int,
        user_id: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> str:

        guild = self.bot.get_guild(guild_id)

        all_messages = self.cache.get_messages(guild_id, start, end)
        messages_for_user = [m for m in all_messages if m["user_id"] == user_id]
        channels = {}
        for message in messages_for_user:
            channel_id = message["channel_id"]
            if channel_id not in channels:
                channels[channel_id] = 0
            channels[channel_id] += 1

        favourite_channel = sorted(channels, key=lambda x: channels[x], reverse=True)[0]
        fav_channel_obj = await guild.fetch_channel(favourite_channel)
        least_fav_channel = sorted(channels, key=lambda x: channels[x], reverse=False)[0]
        least_fav_channel_obj = await guild.fetch_channel(least_fav_channel)

        all_thread_messages = self.cache.get_threaded_messages(guild_id, start, end)
        thread_messages_for_user = [m for m in all_thread_messages if m["user_id"] == user_id]

        if thread_messages_for_user:
            threads = {}
            for message in thread_messages_for_user:
                thread_id = message["channel_id"]
                if channel_id not in threads:
                    threads[thread_id] = 0
                threads[thread_id] += 1
            fav_thread = sorted(threads, key=lambda x: threads[x], reverse=True)[0]
            fav_thread_obj = await guild.fetch_channel(fav_thread)
            least_fav_thread = sorted(threads, key=lambda x: threads[x], reverse=False)[0]
            least_fav_thread_obj = await guild.fetch_channel(least_fav_thread)

        msg = (
            "Here are your stats:\n"
            f"**Messages sent**: {len(messages_for_user)} "
            f"(in `{len(channels)}` channels{f' and `{len(threads)}` threads' if threads else ''})\n"
            f"**Favourite channel**: {fav_channel_obj.mention} (`{channels[favourite_channel]}` messages sent)\n"
            "**Least favourite channel**: "
            f"{least_fav_channel_obj.mention} (`{channels[least_fav_channel]}` messages sent)\n"
        )

        if thread_messages_for_user:
            msg += f"**Favourite thread**: {fav_thread_obj.mention} (`{threads[fav_thread]}` messages sent)\n"
            msg += (
                f"**Least favourite thread**: {least_fav_thread_obj.mention} "
                f"(`{threads[least_fav_thread]}` messages sent)\n"
            )
        
        all_replies = self.cache.get_replies(guild_id, start, end)
        our_messages_with_replies = [m for m in all_replies if m["user_id"] == user_id]
        message_with_our_replies = [m for m in all_replies if any([r for r in m["replies"] if r["user_id"] == user_id])]
        
        replies_received = 0
        for message in our_messages_with_replies:
            for reply in message["replies"]:
                replies_received += 1
        
        replies_given = 0
        for message in message_with_our_replies:
            for reply in message["replies"]:
                if reply["user_id"] != user_id:
                    continue
                replies_given += 1

        msg += f"**Replies generated**: {replies_received}\n"
        msg += f"**Replies given**: {replies_given}\n"

        return msg
