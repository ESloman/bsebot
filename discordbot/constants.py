"""
This file is for static variables throughout the project.
"""

SLOMAN_SERVER_ID = 291508460519161856
BSE_SERVER_ID = 181098823228063764
BSE_BOT_ID = 809505325505576971

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
    "reaction_received",
    "reply_received",
    "wordle",
    "wordle_win"
    "thread_create",
    "react_train",
    "custom_emoji_reaction",
    "custom_emoji",
    "emoji_used",
    "emoji_created",
    "vc_joined",
    "vc_streaming"
]

HUMAN_MESSAGE_TYPES = {
    "message": "Messages",
    "reply": "Replies to messages",
    "attachment": "Attachments sent",
    "role_mention": "Role mentions",
    "channel_mention": "Channel mentions",
    "mention": "Mentions",
    "everyone_mention": "Everyone mentions",
    "gif": "Gifs sent",
    "link": "Links sent",
    "reaction_received": "Reactions received",
    "reply_received": "Replies received",
    "daily": "Daily minimum",
    "wordle": "Wordle",
    "wordle_win": "Wordle Victory",
    "thread_create": "Thread Create",
    "react_train": "Reaction train",
    "custom_emoji_reaction": "Emoji",
    "custom_emoji": "Used a server emoji",
    "emoji_used": "Your server emoji used",
    "emoji_created": "Emoji created",
    "custom_sticker": "Used a server sticker",
    "sticker_used": "Your server sticker used",
    "sticker_created": "Sticker created",
    "vc_joined": "Spent time in VC",
    "vc_streaming": "Spent time streaming",
}

MESSAGE_VALUES = {
    "message": 0.15,
    "reply": 0.5,
    "role_mention": 1,
    "channel_mention": 1,
    "mention": 1,
    "everyone_mention": 1,
    "gif": 0.4,
    "link": 1.2,
    "attachment": 1.2,
    "reaction_received": 2,
    "reply_received": 2,
    "wordle": 2,
    "thread_create": 2,
    "react_train": 1,
    "custom_emoji_reaction": 2,
    "custom_emoji": 1,
    "emoji_used": 2,
    "emoji_created": 5,
    "custom_sticker": 1,
    "sticker_used": 2,
    "sticker_created": 5,
    "vc_joined": 0.0015,
    "vc_streaming": 0.0025
}

WORDLE_VALUES = {
    6: 0,
    5: 1,
    4: 2,
    3: 3,
    2: 5,
    1: 0,
    "X": 0
}

BET_OUTCOME_COUNT_MODIFIER = {
    2: 0.04,
    3: 0.06,
    4: 0.07,
    5: 0.1,
    6: 0.12,
    7: 0.14,
    8: 0.16,
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
    809773876078575636,
    814087061619212299,
    823100959592415262,
    824244254124933150,
    884720128695107594,
]

BSEDDIES_DEVELOPMENT_CHANNEL = 814087061619212299
BSEDDIES_REVOLUTION_CHANNEL = 817061592335122433
BSE_SERVER_INFO_CHANNEL = 823100959592415262
VALORANT_CHAT = 724550853620662302
VALORANT_ROLE = 724885799119880272
GENERAL_CHAT = 181098823228063764

BSEDDIES_KING_ROLES = {
    SLOMAN_SERVER_ID: 322742107460861962,
    BSE_SERVER_ID: 813738204989227008,
}

SERVER_ADMINS = (
    189458414764687360,
    181098573579026433,
    189435778315714560,
    77458304837615616,
    189405043018039297
)

AWS_GAME_SERVER_INSTANCE = "i-04bb3a992e54b1b6f"

MONTHLY_AWARDS_PRIZE = 100
ANNUAL_AWARDS_AWARD = 500
