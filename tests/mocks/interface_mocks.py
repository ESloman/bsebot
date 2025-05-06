"""Mocks our interface functions."""

import contextlib
import copy
import datetime
import pathlib
from difflib import SequenceMatcher

import orjson
from bson import ObjectId

from discordbot.bot_enums import SupporterType

_CURRENT_DIR = pathlib.Path(pathlib.Path(__file__).parents[0])
_CACHE = {}


def get_collection_mock(_: any, name: str) -> str:
    """get_collection mock."""
    return name


def get_database_mock(_: any, name: str) -> str:
    """get_database mock."""
    return name


def _datetime_convert(entry: dict[str, any]) -> None:
    """Convert keys into datetime objects."""
    for key in entry:
        if entry[key] and isinstance(entry[key], list) and isinstance(entry[key][0], dict):
            for part in entry[key]:
                _datetime_convert(part)
            continue
        if key in {
            "created",
            "timestamp",
            "rename_supporter",
            "rename_revolutionary",
            "king_since",
            "last_ad_time",
            "last_remind_me_suggest_time",
            "last_revolution_time",
            "edited",
            "timeout",
            "expired",
        }:
            with contextlib.suppress(ValueError):
                entry[key] = datetime.datetime.strptime(entry[key], "%Y-%m-%dT%H:%M:%S.%f%z")


def mock_user(
    _id: ObjectId = ObjectId(),
    guild_id: int = 123456789,
    name: str = "name",
    uid: str = 123456789,
    points: int = 500,
    king: bool = False,
    daily_eddies: bool = False,
    daily_summary: bool = False,
    summary_detailed_mode: bool = False,
    pending_points: int = 0,
    high_score: int = 1000,
    daily_minimum: int = 4,
    supporter_type: SupporterType = SupporterType.NEUTRAL,
    inactive: bool = False,
) -> dict[str, bool | int | str, SupporterType]:
    """Creates a mock user dictionary with some default values."""
    return locals()


def mock_guild(
    _id: ObjectId = ObjectId(),
    guild_id: int = 123456789,
    name: str = "name",
    owner_id: int = 123456789,
    created: datetime.datetime = datetime.datetime.now(datetime.UTC),
    admins: list[int] | None = None,
) -> dict[str, bool | int | str | list[int]]:
    """Creates a mock guild dictionary with some default values."""
    if admins is None:
        admins = []
    return locals()


def mock_revolution_event(
    _id: ObjectId = ObjectId(),
    guild_id: int = 123456789,
    channel_id: int = 123456789,
    message_id: int = 123456789,
    type: str = "revolution",
    event_id: str = "0001",
    created: datetime.datetime = datetime.datetime.now(datetime.UTC),
    expired: datetime.datetime = datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=4),
    open: bool = False,
    king: int = 123456789,
    chance: int = 30,
    locked_in_eddies: int = 1000,
    points_distributed: int = 1000,
    success: bool = True,
    times_saved: int = 0,
    one_hour: bool = False,
    half_hour: bool = False,
    quarter_hour: bool = False,
    users: list[int] | None = None,
    supporters: list[int] | None = None,
    revolutionaries: list[int] | None = None,
    neutrals: list[int] | None = None,
    locked: list[int] | None = None,
    bribe_offered: bool = False,
    bribe_accepted: bool = False,
) -> dict[str, bool | int | str | list[int]]:
    """Creates a mock revolution event dictionary with some default values."""
    if locked is None:
        locked = []
    if neutrals is None:
        neutrals = []
    if revolutionaries is None:
        revolutionaries = []
    if supporters is None:
        supporters = []
    if users is None:
        users = []
    return locals()


def mock_bot_activity(
    _id: ObjectId = ObjectId(),
    category: str = "playing",
    name: str = "some activity",
    created_by: int = 123456789,
    created: datetime.datetime = datetime.datetime.now(datetime.UTC),
    count: int = 5,
    archived: bool = False,
) -> dict[str, str | int | bool | datetime.datetime]:
    """Creates a mock bot activity dictionary with some default values."""
    return locals()


def query_mock(  # noqa: C901, PLR0912, PLR0915
    collection_name: str, parameters: dict[str, any], *_args: tuple[any], **_kwargs: dict[str, any]
) -> list[dict[str, any]]:
    """Query mock."""
    # load the data
    path = pathlib.Path("mock_data", "bestsummereverpoints", f"{collection_name}.json")
    path = pathlib.Path(_CURRENT_DIR, path)

    # might have cached our data earlier - saves on a little bit of loading time
    # inbetween queries
    if path in _CACHE:
        all_data = _CACHE[path]
    else:
        if not path.exists():
            return []
        all_data = orjson.loads(path.read_text(encoding="utf-8"))
        for entry in all_data:
            _datetime_convert(entry)
        _CACHE[path] = all_data

    # search all data for matching parameters
    _filtered_data = all_data
    for key, value in parameters.items():
        data_to_search = copy.deepcopy(_filtered_data)
        _filtered_data = []
        for data in data_to_search:
            if key not in data and key not in {"replies.timestamp", "reactions.timestamp", "$text", "selectable"}:
                # key not in data - won't match
                continue

            if key in {"replies.timestamp", "reactions.timestamp"}:
                # hard-code how we deal with this for now
                # look at refactoring this method later to deal with this kind of query
                # more dynamically
                first_part = key.split(".")[0]
                if not data.get(first_part, []):
                    continue
                items = data[first_part]
                for item in items:
                    try:
                        data_val = item["timestamp"]
                    except TypeError:
                        data_val = item.timestamp
                    for _key, _value in value.items():
                        match _key:
                            case "$gt":
                                # data_val has got to bigger than _value
                                if data_val > _value and data not in _filtered_data:
                                    _filtered_data.append(data)
                            case "$gte":
                                # data_val has got to bigger or equal that _value
                                if data_val >= _value and data not in _filtered_data:
                                    _filtered_data.append(data)
                            case "$lt":
                                if data_val < _value and data not in _filtered_data:
                                    _filtered_data.append(data)
                continue
            data_val = data.get(key)

            if isinstance(value, dict):
                # handle more complicated queries
                for _key, _value in value.items():
                    match _key:
                        case "$gt":
                            # data_val has got to bigger than _value
                            if data_val > _value:
                                _filtered_data.append(data)
                        case "$gte":
                            # data_val has got to bigger or equal that _value
                            if data_val >= _value:
                                _filtered_data.append(data)
                        case "$lt":
                            if data_val < _value:
                                _filtered_data.append(data)
                        case "$ne":
                            if data_val != _value:
                                _filtered_data.append(data)
                        case "$nin":
                            # data_val can't be in _value
                            if isinstance(data_val, list):
                                # possible for our data_val to be a list
                                for item in data_val:
                                    if item in _value:
                                        break
                                else:
                                    _filtered_data.append(data)
                            elif data_val not in _value:
                                _filtered_data.append(data)
                        case "$search" if key == "$text":
                            if SequenceMatcher(None, _value, data.get("content", "")).ratio() > 0.5:
                                _filtered_data.append(data)
                continue

            if isinstance(data_val, list) and value in data_val:
                # if data_val is list then check our value is in it
                _filtered_data.append(data)

            if data_val == value:
                _filtered_data.append(data)

    return _filtered_data


def update_mock(*_args: tuple[any], **kwargs: dict[any]) -> None:
    """Update mock."""


def insert_mock(*_args: tuple[any], **kwargs: dict[any]) -> list[ObjectId]:
    """Insert mock."""
    return [ObjectId() for _ in range(1)]
