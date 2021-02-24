"""
A file for enums
"""

from enum import auto, IntEnum


class TransactionTypes(IntEnum):
    """
    TransactionTypes are the type of "transactions" that can take place when a user gains/loses eddies.
    """
    HISTORY_START = 1
    BET_PLACE = 2
    BET_WIN = 3
    GIFT_GIVE = 4
    GIFT_RECEIVE = 5
    DAILY_SALARY = 6
    USER_CREATE = 7
    OVERRIDE = 99
