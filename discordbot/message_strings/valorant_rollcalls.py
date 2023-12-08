"""File for daily valorant message rollcall messages.

when sending a valorant rollcall message
message will be chosen randomly, but based on some dynamically created odds
use a tuple to hardcode some odds
the '{role}' bit is where the valorant role mention will be inserted
to add a new one, simply add a new line
"""

MESSAGES = [
    "Anyone playing after-work {role} today?",
    "Who's about for after-work {role}?",
    "Anyone wanna get salty playing {role}?",
    "Who's gonna grind some `Lotus` today {role}?",
    "Anyone want to lose some RR {role}?",
    "Who wants to roll some fat 1s playing {role}?",
    "Can we get an after-work 5-stack today for {role}?",
    "My pp is soft, but my Valorant is hard. Someone play a game with me, {role}?",
    "Jingle bells, jingle bells, jingle all the IT'S TIME TO PLAY VALORANT {role}",
    "Valorant? Valorant? VALORANT? VALROARANT? RAVALROANT? {role}",
    "I'm a little bot, it's time to get mad and play {role}?",
    "# Balls. {role}",
    # HARD-CODED ODDS EXAMPLE
    # tuple with message string as first item, chance (roughly out of 100) as a float
]
