"""Contants.

This file contains a variety of different variables whose values aren't going to change. We use these in various places
throughout the codebase so we define them here.
"""

SLOMAN_SERVER_ID = 291508460519161856
BSE_SERVER_ID = 181098823228063764
BSE_BOT_ID = 809505325505576971

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
    "wordle_winthread_create",
    "react_train",
    "custom_emoji_reaction",
    "custom_emoji",
    "emoji_used",
    "emoji_created",
    "vc_joined",
    "vc_streaming",
    "voice_message",
    "wordle_word_used",
    "alphabetical",
]

# a mapping of the above message types to a more human readable/understandable version
HUMAN_MESSAGE_TYPES = {
    "alphabetical": "Alphabetical messages",
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
    "custom_emoji": "Used a custom emoji",
    "server_emoji": "Used a server emoji",
    "emoji_used": "Your server emoji used",
    "emoji_created": "Emoji created",
    "custom_sticker": "Used a sticker",
    "server_sticker": "Used a server sticker",
    "sticker_used": "Your server sticker used",
    "sticker_created": "Sticker created",
    "vc_joined": "Spent time in VC",
    "vc_streaming": "Spent time streaming",
    "voice_message": "Voice Message",
    "wordle_word_used": "Used daily Wordle word",
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
    "server_emoji": 2,
    "emoji_used": 2,
    "emoji_created": 5,
    "custom_sticker": 1,
    "sticker_used": 2,
    "sticker_created": 5,
    "server_sticker": 2,
    "vc_joined": 0.0015,
    "vc_streaming": 0.0025,
    "voice_message": 4,
    "wordle_word_used": 2,
    "alphabetical": 0.5,
}

# the number of eddies a user received for each wordle score
WORDLE_VALUES = {6: 1, 5: 2, 4: 3, 3: 4, 2: 10, 1: 25, "X": 1}

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

# amount of eddies on a bet that we will just return on winning
SMALL_BET_AMOUNT = 10

# leaderboard stuff
# max number of users to filter by user points
MIN_USERS_FILTER = 10
# the eddies total to filter users out with
USER_POINTS_FILTER = 10

# the user that created the bot (aka ESloman)
CREATOR = 189458414764687360

# BSE specific channel IDs
BSEDDIES_REVOLUTION_CHANNEL = 817061592335122433
GENERAL_CHAT = 181098823228063764
JERK_OFF_CHAT = 470696533873000449
GENERAL_VC_CHAT = 181098823232258048

# the bseddies awards money
MONTHLY_AWARDS_PRIZE = 100
ANNUAL_AWARDS_AWARD = 500
STAT_DATETIME_FORMAT = "%b %y"

# regex for recognising a message is wordle
WORDLE_REGEX = r"Wordle \d?\,?\d\d\d [\dX]/\d\n\n"
# regex for getting wordle score
WORDLE_SCORE_REGEX = r"[\dX]/\d"

# cool down in seconds for marvel ad messages
MARVEL_AD_COOLDOWN = 3600
# cool down in seconds for remind me reminders
REMIND_ME_COOLDOWN = 3600
# cool down in seconds for rigged messages
RIGGED_COOLDOWN = 300

# max bet title display length
BET_TITLE_DISPLAY_LENTH = 100
