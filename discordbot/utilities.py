"""File for other small and useful classes that we may need in other parts of the code."""

import re

from pymongo.errors import OperationFailure

from mongo.bsepoints.interactions import UserInteractions


def convert_time_str(time_str: str) -> int:
    """Converts a given time string into the number of seconds.

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


def calculate_message_odds(
    interactions: UserInteractions,
    guild_id: int,
    message_list: list[str],
    split: str,
    main_indexes: list[int],
) -> list[tuple[str, float]]:
    """Given a list of messages, calculates what the odds should be of each one getting picked.

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

            if (
                len(message) != 2  # noqa: PLR2004
                or not isinstance(message[0], str)
                or not isinstance(message[1], int | float)
            ):
                # tuple isn't correctly formatted - skip this one
                continue

            odds.append(message)
            continue

        parts = message.split(split)
        main_bit = sorted(parts, key=len, reverse=True)[0]

        try:
            results = interactions.query({"guild_id": guild_id, "is_bot": True, "$text": {"$search": message}})
            results = [result for result in results if main_bit in result.content]
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
