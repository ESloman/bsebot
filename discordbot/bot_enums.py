"""
A file for enums
"""

from enum import IntEnum


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
    BET_REFUND = 8
    LOAN_TAKE = 9
    LOAN_REPAYMENT = 10
    LOAN_COLLECTION = 11
    ADMIN_GIVE = 12
    ADMIN_TAKE = 13
    POINT_ROT_LOSS = 14
    POINT_ROT_GAIN = 15
    REV_TICKET_BUY = 16
    REV_TICKET_WIN = 17
    REV_TICKET_KING_WIN = 18
    OVERRIDE = 99


class ActivityTypes(IntEnum):
    """
    ActivityTypes are types of activity that we are tracking (that aren't transactions)
    """
    KING_GAIN = 1
    KING_LOSS = 2
    LOAN_TAKE = 3
    LOAN_REPAYMENT = 4
    LOAN_COLLECTION = 5
