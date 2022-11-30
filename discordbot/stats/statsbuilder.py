import datetime
from typing import Tuple

import discord

from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.stats.userstatsclasses import UserStatsGatherer
from mongo.bsedataclasses import Awards
from mongo.bsepoints import UserPoints


class PersonalStatsBuilder:
    def __init__(self, bot: discord.Client, logger):
        self.bot = bot
        self.logger = logger
        self.stats = UserStatsGatherer(self.logger)

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

        channel_stats = self.stats.user_message_and_channel_stats(user_id, guild_id, start, end)

        fav_channel_obj = await guild.fetch_channel(channel_stats["favourite_channel"])
        least_fav_channel_obj = await guild.fetch_channel(channel_stats["least_favourite_channel"])

        if channel_stats["thread_number"]:
            fav_thread_obj = await guild.fetch_channel(channel_stats["favourite_thread"])
            least_fav_thread_obj = await guild.fetch_channel(channel_stats["least_favourite_thread"])
            
        channel_text = f"`{channel_stats['total_channels']}` channels"
        if channel_stats["thread_number"]:
            channel_text += f" and `{channel_stats['total_threads']}` threads"

        msg = (
            "Here are your stats:\n"
            f"**Messages sent**: {channel_stats['number']} (in {channel_text})\n"
            f"**Favourite channel**: {fav_channel_obj.mention} (`{channel_stats['fc_messages']}` messages sent)\n"
            "**Least favourite channel**: "
            f"{least_fav_channel_obj.mention} (`{channel_stats['lfc_messages']}` messages sent)\n"
        )

        if channel_stats["thread_number"]:
            msg += f"**Favourite thread**: {fav_thread_obj.mention} (`{channel_stats['ft_messages']}` messages sent)\n"
            msg += (
                f"**Least favourite thread**: {least_fav_thread_obj.mention} "
                f"(`{channel_stats['lft_messages']}` messages sent)\n"
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
