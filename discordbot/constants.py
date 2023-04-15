
"""
This file contains a variety of different variables whose values aren't going to change. We use these in various places
throughout the codebase so we define them here.
"""

SLOMAN_SERVER_ID = 291508460519161856
BSE_SERVER_ID = 181098823228063764
BSE_BOT_ID = 809505325505576971

# bots that aren't ours
BOT_IDS = [
    439103207210352650,  # patch bot
    272937604339466240  # craig bot
]

# the types of 'message' or 'interaction'
# mostly used for calculating user salaries
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
    "vc_streaming",
    "voice_message"
]

# a mapping of the above message types to a more human readable/understandable version
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
    "voice_message": "Voice Message"
}

# a mapping of the above message types; and how many eddies they are worth for each individual occurence
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
    "vc_streaming": 0.0025,
    "voice_message": 4
}

# the number of eddies a user received for each wordle score
WORDLE_VALUES = {
    6: 1,
    5: 2,
    4: 3,
    3: 4,
    2: 10,
    1: 1,
    "X": 1
}

# bet outcome coefficient
BET_OUTCOME_COUNT_MODIFIER = {
    2: 0.04,
    3: 0.06,
    4: 0.07,
    5: 0.1,
    6: 0.12,
    7: 0.14,
    8: 0.16,
}

# the user that created the bot (aka ESloman)
CREATOR = 189458414764687360

# BSE boys role
THE_BOYS_ROLE = 724888354004533258
# BSE valorant role
VALORANT_ROLE = 724885799119880272

# BSE specific channel IDs
BSEDDIES_REVOLUTION_CHANNEL = 817061592335122433
VALORANT_CHAT = 724550853620662302
GENERAL_CHAT = 181098823228063764
JERK_OFF_CHAT = 470696533873000449

# KING roles
BSEDDIES_KING_ROLES = {
    SLOMAN_SERVER_ID: 1066004383705337936,
    BSE_SERVER_ID: 813738204989227008,
}

# the bseddies awards money
MONTHLY_AWARDS_PRIZE = 100
ANNUAL_AWARDS_AWARD = 500

# regex for recognising a message is wordle
WORDLE_REGEX = r"Wordle \d?\d\d\d [\dX]/\d\n\n"
# regex for getting wordle score
WORDLE_SCORE_REGEX = r"[\dX]/\d"

# cool down in seconds for marvel ad messages
MARVEL_AD_COOLDOWN = 3600
