
"""
File for other small and useful classes that we may need in other parts of the code
"""

import datetime
import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler

from pymongo.errors import OperationFailure

from mongo.bsepoints.interactions import UserInteractions


class PlaceHolderLogger():
    """
    Placeholder logger for when we don't have a logging object
    replaces logging functions with just printing
    """
    @staticmethod
    def info(msg: str) -> None:
        print(msg)

    @staticmethod
    def debug(msg: str) -> None:
        print(msg)

    @staticmethod
    def warning(msg: str) -> None:
        print(msg)


class _ColourFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m[%(asctime)s]\x1b[0m {colour}[%(levelname)s] \x1b[0m\x1b[35m%(funcName)8s:\x1b[0m %(message)s"
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def create_logger(level: int = None) -> logging.Logger:
    """
    Creates a simple logger to use throughout the bot
    :return: Logger object
    """
    if not level:
        level = logging.DEBUG

    fol = os.path.join(os.path.expanduser("~"), "bsebotlogs")
    if not os.path.exists(fol):
        os.makedirs(fol)

    _logger = logging.getLogger("bsebot")
    _logger.setLevel(level)

    formatting = "[%(asctime)s] [%(levelname)8s] %(funcName)s: %(message)s"
    formatter = logging.Formatter(formatting)
    colour_formatter = _ColourFormatter()

    # this makes sure we're logging to the standard output too
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(colour_formatter)

    # this makes sure we're logging to a file
    file_handler = RotatingFileHandler(
        os.path.join(fol, "bsebot.log"), maxBytes=10485760, backupCount=1
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(stream_handler)
    _logger.addHandler(file_handler)

    return _logger


def convert_time_str(time_str: str) -> int:
    """
    Converts a given time string into the number of seconds.

    Time strings are strings in the format:
    - 1w7d24h60m60s

    Where each unit is optional to provide and the numbers can be as large as required.

    Args:
        time_str (str): the time string to convert

    Returns:
        int: total seconds
    """
    # dict for converting a unit into number of seconds for each unit
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
    # this pattern looks for days, hours, minutes, seconds in the string, etc
    regex_pattern = r"^(?P<week>\d+w)?(?P<day>\d+d)?(?P<hour>\d+h)?(?P<minute>\d+m)?(?P<second>\d+s)?"
    matches = re.match(regex_pattern, time_str)
    total_time = 0
    for group in matches.groups():
        if not group:
            continue
        unit = group[-1]
        val = int(group[:-1])
        amount = val * time_dict[unit]
        total_time += amount
    return total_time


def get_utc_offset() -> int:
    d = datetime.datetime.now(datetime.timezone.utc).astimezone()
    utc_offset = d.utcoffset() // datetime.timedelta(seconds=1)
    return utc_offset


def add_utc_offset(date: datetime.datetime) -> datetime.datetime:
    offset = get_utc_offset()
    new_date = date - datetime.timedelta(seconds=offset)
    return new_date


def is_utc(date: datetime.datetime) -> bool:
    now_utc = datetime.datetime.now(tz=datetime.timezone.utc)
    return now_utc.hour == date.hour


def calculate_message_odds(
    interactions: UserInteractions,
    guild_id: int,
    message_list: list[str],
    split: str,
    main_indexes: list[int],
) -> list[tuple[str, float]]:
    """
    Given a list of messages, calculates what the odds should be of each one getting picked.
    This searches for previously used instances of those messages and then works out which ones should have
    higher/lower odds.

    Args:
        interactions (UserInteractions): UserInteractions class for queries
        guild_id (int): the guild ID
        message_list (list[str]): the list of messages to get odds for
        split (str): the marker to split the list of messages on to validate text search results
        main_indexes (list[int]): the indexes of the messages that get extra odds

    Returns:
        list[tuple[str, float]]: list of messages tuples with the original string and the float percentage chance
    """

    # work out message odds
    odds = []
    totals = {}
    # get the number of times each rollcall message has been used
    for message in message_list:

        if type(message) is tuple:
            # if message type is tuple
            # assume odds are already set for it

            if len(message) != 2 or type(message[0]) is not str or type(message[1]) not in [int, float]:
                # tuple isn't correctly formatted - skip this one
                continue

            odds.append(message)
            continue

        parts = message.split(split)
        main_bit = sorted(parts, key=lambda x: len(x), reverse=True)[0]

        try:
            results = interactions.query(
                {
                    "guild_id": guild_id,
                    "is_bot": True,
                    "$text": {"$search": message}
                }
            )
            results = [result for result in results if main_bit in result["content"]]
        except OperationFailure:
            totals[message] = 0
            continue

        totals[message] = len(results)

    # work out the weight that a given message should be picked
    total_values = sum(totals.values())
    for message in message_list:
        _times = totals[message]
        _chance = (1 - (_times / total_values)) * 100

        # give greater weighting to standard messages
        if message_list.index(message) in main_indexes:
            _chance += 25

        # give greater weighting to those with 0 uses so far
        if _times == 0:
            _chance += 25

        odds.append((message, _chance))

    return odds
