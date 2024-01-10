"""Mocks our interface functions."""

import copy
import json
import pathlib

from bson import ObjectId

_CURRENT_DIR = pathlib.Path(pathlib.Path(__file__).parents[0])
_CACHE = {}


def get_collection_mock(_: any, name: str) -> str:
    """get_collection mock."""
    return name


def get_database_mock(_: any, name: str) -> str:
    """get_database mock."""
    return name


def query_mock(collection_name: str, parameters: dict, *_args: tuple[any], **_kwargs: dict[str, any]) -> list:
    """Query mock."""
    # load the data
    path = pathlib.Path("mock_data", "bestsummereverpoints", f"{collection_name}.json")
    path = pathlib.Path(_CURRENT_DIR, path)

    # might have cached our data earlier - saves on a little bit of loading time
    # inbetween queries
    if path in _CACHE:
        all_data = _CACHE[path]
    else:
        with open(path, encoding="utf-8") as json_file:
            all_data = json.load(json_file)
            _CACHE[path] = all_data

    # search all data for matching parameters
    _filtered_data = all_data
    for key, value in parameters.items():
        data_to_search = copy.deepcopy(_filtered_data)
        _filtered_data = []
        for data in data_to_search:
            if key not in data:
                # key not in data - won't match
                continue

            data_val = data.get(key)
            if data_val == value:
                _filtered_data.append(data)

    return _filtered_data


def update_mock(*_args: tuple[any], **kwargs: dict[any]) -> None:
    """Update mock."""


def insert_mock(*_args: tuple[any], **kwargs: dict[any]) -> list[ObjectId]:
    """Insert mock."""
    return [ObjectId() for _ in range(1)]
