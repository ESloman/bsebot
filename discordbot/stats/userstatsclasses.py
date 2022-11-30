import datetime
from typing import Tuple

from discordbot.bot_enums import ActivityTypes, AwardsTypes, TransactionTypes
from discordbot.constants import ANNUAL_AWARDS_AWARD, BSE_BOT_ID, JERK_OFF_CHAT, MONTHLY_AWARDS_PRIZE
from discordbot.stats.statsdatacache import StatsDataCache
from discordbot.stats.statsdataclasses import UserMessageChannelStat


class UserStatsGatherer:
    def __init__(self, logger) -> None:
        self.logger = logger
        self.cache = StatsDataCache(self.annual)

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

    def user_message_and_channel_stats(
        self,
        user_id: int,
        guild_id: int,
        start: datetime.datetime,
        end: datetime.datetime
    ) -> UserMessageChannelStat:
        """Calculates user stats for messages and channels for the given time frame in the given guild

        Args:
            user_id (int): The user ID
            guild_id (int): the guild ID
            start (datetime.datetime): start time frame
            end (datetime.datetime): end time frame

        Returns:
            UserMessageChannelStat: the Stat object
        """
        all_messages = self.cache.get_messages(guild_id, start, end)
        all_thread_messages = self.cache.get_threaded_messages(guild_id, start, end)

        messages_for_user = [m for m in all_messages if m["user_id"] == user_id]
        thread_messages_for_user = [m for m in all_thread_messages if m["user_id"] == user_id]

        channels = {}
        for message in messages_for_user:
            channel_id = message["channel_id"]
            if channel_id not in channels:
                channels[channel_id] = 0
            channels[channel_id] += 1

        favourite_channel = sorted(channels, key=lambda x: channels[x], reverse=True)[0]
        least_fav_channel = sorted(channels, key=lambda x: channels[x], reverse=False)[0]

        threads = {}
        for message in thread_messages_for_user:
            thread_id = message["channel_id"]
            if channel_id not in threads:
                threads[thread_id] = 0
            threads[thread_id] += 1

        fav_thread = 0
        least_fav_thread = 0
        if threads:
            fav_thread = sorted(threads, key=lambda x: threads[x], reverse=True)[0]
            least_fav_thread = sorted(threads, key=lambda x: threads[x], reverse=False)[0]

        stat = UserMessageChannelStat(
            user_id=user_id,
            number=len(all_messages),
            total_channels=len(channels),
            favourite_channel=favourite_channel,
            fc_messages=channels[favourite_channel],
            least_favourite_channel=least_fav_channel,
            lfc_messages=channels[least_fav_channel],
            thread_number=len(thread_messages_for_user),
            total_threads=len(threads),
            favourite_thread=fav_thread,
            ft_messages=threads[fav_thread],
            least_favourite_thread=least_fav_thread,
            lft_messages=threads[least_fav_thread]
        )

        return stat
