import datetime
import json
import logging
import math
import os
import sys

from collections import Counter
from logging.handlers import RotatingFileHandler

from discordbot.bot_enums import TransactionTypes
from discordbot.constants import MESSAGE_TYPES, MESSAGE_VALUES
from mongo.bsepoints import UserPoints, UserInteractions


class BSEddiesManager(object):
    """
    Class for managing passive eddie gain.
    """
    def __init__(self):
        self.user_interactions = UserInteractions()
        self.user_points = UserPoints()
        self.logger = self._create_logger()

    @staticmethod
    def _create_logger():
        """
        Simple method to create a logger.
        :return:
        """
        fol = os.path.join(os.path.expanduser("~"), "bsebotlogs")
        if not os.path.exists(fol):
            os.makedirs(fol)

        _logger = logging.getLogger("eddie_manager")
        _logger.setLevel(logging.DEBUG)

        formatting = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(formatting)

        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setFormatter(formatter)

        file_handler = RotatingFileHandler(
            os.path.join(fol, "eddie_manager.log"), maxBytes=10485760, backupCount=1
        )
        file_handler.setFormatter(formatter)

        _logger.addHandler(stream_handler)
        _logger.addHandler(file_handler)
        return _logger

    @staticmethod
    def get_datetime_objects():
        """
        Get's the datetime START and END of yesterday
        :return:
        """
        now = datetime.datetime.now()
        yesterday = now - datetime.timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)
        return start, end

    def _calc_eddies(self, counter, start=4):
        """
        Quick function to loop over the message types and work out an amount of BSEddies the user will gain
        :param counter:
        :return:
        """
        points = start
        for message_type in MESSAGE_TYPES:
            if val := counter.get(message_type):
                t_points = val * MESSAGE_VALUES[message_type]
                points += t_points
                self.logger.info(f"{t_points} for {message_type}")
        return points

    def calc_individual(self, user, user_dict, user_results, guild_id, real=False):

        minimum = user_dict.get("daily_minimum", 4)

        if not user_results:
            if minimum == 0:
                return 0

            if minimum < 0:
                if real:
                    self.user_points.set_daily_minimum(user, guild_id, 0)
                return 0

            minimum -= 1
            if real:
                self.user_points.decrement_daily_minimum(user, guild_id, 1)
            if minimum == 0:
                return 0
        else:
            if minimum != 4:
                minimum = 4
                if real:
                    self.user_points.set_daily_minimum(user, guild_id, 4)

        message_types = [r["message_type"] for r in user_results]

        # add reaction_received events
        for message in user_results:
            if reactions := message.get("reactions"):
                for reaction in reactions:
                    if reaction["user_id"] == user:
                        continue
                    message_types.append("reaction_received")

        count = Counter(message_types)
        eddies_gained = self._calc_eddies(count, minimum)

        eddies_gained = math.floor(eddies_gained)
        return eddies_gained

    def give_out_eddies(self, guild_id=181098823228063764):
        """
        Takes all the user IDs for a server and distributes BSEddies to them
        :param guild_id:
        :return:
        """
        start, end = self.get_datetime_objects()

        # query gets all messages yesterday
        results = self.user_interactions.query(
            {
                "guild_id": guild_id,
                "timestamp": {"$gt": start, "$lt": end}
            }
        )

        users = self.user_points.get_all_users_for_guild(guild_id)
        users = [u for u in users if not u.get("inactive")]
        user_ids = [u["uid"] for u in users]
        user_dict = {u["uid"]: u for u in users}

        eddie_gain_dict = {"guild": guild_id}
        for user in user_ids:
            self.logger.info(f"processing {user}")

            user_results = [r for r in results if r["user_id"] == user]

            eddies_gained = self.calc_individual(user, user_dict[user], user_results, guild_id, True)

            if eddies_gained == 0:
                continue

            self.user_points.increment_points(user, guild_id, eddies_gained)
            eddie_gain_dict[user] = eddies_gained
            self.user_points.append_to_transaction_history(
                user,
                guild_id,
                {
                    "type": TransactionTypes.DAILY_SALARY,
                    "amount": eddies_gained,
                    "timestamp": datetime.datetime.now(),
                }
            )
            self.logger.info(f"{user} gained {eddies_gained}")

        with open(os.path.join(os.path.expanduser("~"), "eddies_gained.json"), "w+") as f:
            json.dump(eddie_gain_dict, f)


if __name__ == "__main__":
    e = BSEddiesManager()
    e.give_out_eddies()
