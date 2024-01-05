"""Mocks for dataclasses."""

from bson import ObjectId

from mongo.datatypes.bet import BetterDB, OptionDB


def get_user_inputs() -> list[dict]:
    """Returns a bunch of user inputs."""
    return [
        {
            "_id": ObjectId("602d033b1619eb379f5c5f1a"),
            "uid": 77458304837615616,
            "guild_id": 181098823228063764,
            "points": 59867,
            "pending_points": -14,
            "inactive": False,
            "daily_eddies": True,
            "king": False,
            "last_cull_time": None,
            "high_score": 60329,
            "cull_warning": False,
            "daily_minimum": 4,
            "supporter_type": 1,
            "name": "poo",
        },
        {
            "_id": ObjectId("602d033b1619eb379f5c5f1f"),
            "uid": 189458414764687360,
            "guild_id": 181098823228063764,
            "points": 21279,
            "pending_points": 12,
            "daily_eddies": True,
            "last_cull_time": None,
            "high_score": 42789,
            "cull_warning": False,
            "king": False,
            "daily_minimum": 4,
            "supporter_type": 1,
            "name": "esloman",
            "daily_summary": True,
        },
    ]


def get_bet_option_inputs() -> list[dict]:
    """Returns a bunch of bet option inputs."""
    return [{"val": "Ben"}, {"val": "Pook"}, {"val": "Ross"}, {"val": "Sheldon"}, {"val": "Sloman"}]


def get_bet_better_inputs() -> list[dict]:
    """Returns a bunch of bet better inputs."""
    return [
        {
            "user_id": 189458414764687360,
            "emoji": "2️⃣",
            "first_bet": "2023-12-19T14:30:27.654+0000",
            "last_bet": "2023-12-19T14:30:27.654+0000",
            "points": 1757,
        },
        {
            "user_id": 181098573579026433,
            "emoji": "4️⃣",
            "first_bet": "2023-12-22T09:46:21.645+0000",
            "last_bet": "2023-12-22T09:46:21.645+0000",
            "points": 13615,
        },
        {
            "user_id": 189405043018039297,
            "emoji": "4️⃣",
            "first_bet": "2023-12-23T16:39:26.730+0000",
            "last_bet": "2023-12-23T16:39:26.730+0000",
            "points": 13055,
        },
        {
            "user_id": 189435778315714560,
            "emoji": "2️⃣",
            "first_bet": "2023-12-29T16:36:21.014+0000",
            "last_bet": "2023-12-29T16:36:21.014+0000",
            "points": 2000,
        },
        {
            "user_id": 77458304837615616,
            "emoji": "2️⃣",
            "first_bet": "2023-12-29T16:38:08.504+0000",
            "last_bet": "2023-12-29T16:38:08.504+0000",
            "points": 26848,
        },
    ]


def get_bet_inputs() -> list[dict]:
    """Returns a bunch of bet inputs."""
    return [
        {
            "_id": ObjectId("6581a8df374e2e73c4a70c08"),
            "bet_id": "0580",
            "guild_id": 181098823228063764,
            "user": 189458414764687360,
            "title": "Who will be wordle _loser_ of 2023?",
            "options": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"],
            "created": "2023-12-19T14:29:51.241+0000",
            "timeout": "2023-12-30T14:29:50.955+0000",
            "active": False,
            "betters": {
                "189458414764687360": BetterDB(
                    user_id=189458414764687360,
                    emoji="2️⃣",
                    first_bet="2023-12-19T14:30:27.654+0000",
                    last_bet="2023-12-19T14:30:27.654+0000",
                    points=1757,
                ),
                "181098573579026433": BetterDB(
                    user_id=181098573579026433,
                    emoji="4️⃣",
                    first_bet="2023-12-22T09:46:21.645+0000",
                    last_bet="2023-12-22T09:46:21.645+0000",
                    points=13615,
                ),
                "189405043018039297": BetterDB(
                    user_id=189405043018039297,
                    emoji="4️⃣",
                    first_bet="2023-12-23T16:39:26.730+0000",
                    last_bet="2023-12-23T16:39:26.730+0000",
                    points=13055,
                ),
                "189435778315714560": BetterDB(
                    user_id=189435778315714560,
                    emoji="2️⃣",
                    first_bet="2023-12-29T16:36:21.014+0000",
                    last_bet="2023-12-29T16:36:21.014+0000",
                    points=2000,
                ),
                "77458304837615616": BetterDB(
                    user_id=77458304837615616,
                    emoji="2️⃣",
                    first_bet="2023-12-29T16:38:08.504+0000",
                    last_bet="2023-12-29T16:38:08.504+0000",
                    points=26848,
                ),
            },
            "result": ["2️⃣"],
            "option_dict": {
                "1️⃣": OptionDB(val="Ben"),
                "2️⃣": OptionDB(val="Pook"),
                "3️⃣": OptionDB(val="Ross"),
                "4️⃣": OptionDB(val="Sheldon"),
                "5️⃣": OptionDB(val="Sloman"),
            },
            "channel_id": 817061592335122433,
            "message_id": 1186676778517921922,
            "private": False,
            "updated": "2023-12-19T14:29:51.241+0000",
            "users": [
                189458414764687360,
                181098573579026433,
                189405043018039297,
                189435778315714560,
                77458304837615616,
            ],
            "option_vals": ["Ben", "Pook", "Ross", "Sheldon", "Sloman"],
            "closed": "2024-01-03T12:02:20.158+0000",
            "winners": {"189458414764687360": 11960, "189435778315714560": 12440, "77458304837615616": 55155},
        },
        {
            "_id": ObjectId("6581a8df374e2e73c4a70c08"),
            "bet_id": "0581",
            "guild_id": 181098823228063764,
            "user": 189458414764687360,
            "title": "Who will be wordle _winner_ of 2023?",
            "options": ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"],
            "created": "2023-12-19T14:29:51.241+0000",
            "timeout": "2023-12-30T14:29:50.955+0000",
            "active": True,
            "betters": {
                "189458414764687360": BetterDB(
                    user_id=189458414764687360,
                    emoji="2️⃣",
                    first_bet="2023-12-19T14:30:27.654+0000",
                    last_bet="2023-12-19T14:30:27.654+0000",
                    points=1757,
                ),
                "181098573579026433": BetterDB(
                    user_id=181098573579026433,
                    emoji="4️⃣",
                    first_bet="2023-12-22T09:46:21.645+0000",
                    last_bet="2023-12-22T09:46:21.645+0000",
                    points=13615,
                ),
                "189405043018039297": BetterDB(
                    user_id=189405043018039297,
                    emoji="4️⃣",
                    first_bet="2023-12-23T16:39:26.730+0000",
                    last_bet="2023-12-23T16:39:26.730+0000",
                    points=13055,
                ),
                "189435778315714560": BetterDB(
                    user_id=189435778315714560,
                    emoji="2️⃣",
                    first_bet="2023-12-29T16:36:21.014+0000",
                    last_bet="2023-12-29T16:36:21.014+0000",
                    points=2000,
                ),
                "77458304837615616": BetterDB(
                    user_id=77458304837615616,
                    emoji="2️⃣",
                    first_bet="2023-12-29T16:38:08.504+0000",
                    last_bet="2023-12-29T16:38:08.504+0000",
                    points=26848,
                ),
            },
            "result": None,
            "option_dict": {
                "1️⃣": OptionDB(val="Ben"),
                "2️⃣": OptionDB(val="Pook"),
                "3️⃣": OptionDB(val="Ross"),
                "4️⃣": OptionDB(val="Sheldon"),
                "5️⃣": OptionDB(val="Sloman"),
            },
            "channel_id": 817061592335122433,
            "message_id": 1186676778517921922,
            "private": False,
            "updated": "2023-12-19T14:29:51.241+0000",
            "users": [
                189458414764687360,
                181098573579026433,
                189405043018039297,
            ],
            "option_vals": ["Ben", "Pook", "Ross", "Sheldon", "Sloman"],
            "closed": None,
        },
    ]
