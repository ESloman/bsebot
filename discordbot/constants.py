"""
This file is for static variables throughout the project.
"""

SLOMAN_SERVER_ID = 291508460519161856
BSE_SERVER_ID = 181098823228063764


MESSAGE_TYPES = [
    "message",
    "reply",
    "attachment",
    "role_mention",
    "channel_mention",
    "mention",
    "everyone_mention",
    "gif",
    "link",
]

MESSAGE_VALUES = {
    "message": 0.1,
    "reply": 0.2,
    "role_mention": 1,
    "channel_mention": 0.5,
    "mention": 0.25,
    "everyone_mention": 1,
    "gif": 0.4,
    "link": 1,
    "attachment": 1,
}

BETA_USERS = [
    181098573579026433,
    189458414764687360,
    77458304837615616,
    189405043018039297
]

CREATOR = 189458414764687360

THE_BOYS_ROLE = 724888354004533258

PRIVATE_CHANNEL_IDS = [
    181098823228063764,
    470696533873000449,
    651566692144775168,
    725410607997780150,
    728202427504787456,
    784347380798717972,
    809773876078575636
]


BSEDDIES_KING_ROLES = {
    SLOMAN_SERVER_ID: 322742107460861962,
    BSE_SERVER_ID: 813738204989227008,
}
