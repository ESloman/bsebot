import datetime
import json
import math
import os
from collections import Counter

from discordbot.constants import MESSAGE_TYPES, MESSAGE_VALUES
from mongo.bsepoints import UserPoints, UserInteractions


class BSEddiesManager(object):
    """
    Class for managing passive eddie gain.
    """
    def __init__(self):
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()

    @staticmethod
    def _get_datetime_objects():
        now = datetime.datetime.now()
        # yesterday = now - datetime.timedelta(days=1)
        yesterday = now
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)
        return start, end

    @staticmethod
    def _calc_eddies(counter):
        points = 5
        for message_type in MESSAGE_TYPES:
            if val := counter.get(message_type):
                t_points = val * MESSAGE_VALUES[message_type]
                points += t_points
                print(f"{t_points} for {message_type}")
        return points

    def give_out_eddies(self, guild_id=181098823228063764):
        """

        :param guild_id:
        :return:
        """
        start, end = self._get_datetime_objects()

        # query gets all messages yesterday
        results = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end}
            }
        )

        user_ids = list(set([r["user_id"] for r in results]))
        eddie_gain_dict = {"guild": guild_id}
        for user in user_ids:
            print(f"processing {user}")
            user_results = [r for r in results if r["user_id"] == user]
            message_types = [r["message_type"] for r in user_results]
            count = Counter(message_types)
            eddies_gained = self._calc_eddies(count)
            eddies_gained = math.ceil(eddies_gained)
            eddie_gain_dict[user] = eddies_gained
            print(f"{user} gained {eddies_gained}")

        with open(os.path.join(os.path.expanduser("~"), "eddies_gained.json"), "w+") as f:
            json.dump(eddie_gain_dict, f)


if __name__ == "__main__":
    e = BSEddiesManager()
    e.give_out_eddies()
