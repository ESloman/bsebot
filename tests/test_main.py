"""Tests our main.py file."""

import os
from unittest import mock

import pytest

from discordbot import main
from mongo import interface
from tests.mocks import interface_mocks


class TestMain:
    """Tests our main.py file."""

    def test_main_no_token(self) -> None:
        """Tests main function with no token."""
        main.DEBUG_MODE = True
        main.TOKEN = None
        with pytest.raises(SystemExit):
            main._main()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_main(self) -> None:
        """Tests main function."""
        main.DEBUG_MODE = True
        main.TOKEN = "token"
        with mock.patch.object(main.BSEBot, "run"):
            main._main()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.dict(os.environ, {"MONGODB_IP": "localhost"})
    def test_main_with_mongo_ip(self) -> None:
        """Tests main function with mongo ip set through an environment variable."""
        main.DEBUG_MODE = True
        main.TOKEN = "token"
        with mock.patch.object(main.BSEBot, "run"):
            main._main()

    @pytest.mark.parametrize("get_key", [None, "some_val"])
    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    def test_main_giphy_token(self, get_key: str | None) -> None:
        """Tests main function with various giphy token .env values."""
        main.DEBUG_MODE = True
        main.TOKEN = "token"
        with mock.patch.object(main.BSEBot, "run"), mock.patch.object(main.dotenv, "get_key", new=lambda *_: get_key):  # noqa: PT008
            main._main()

    @mock.patch.object(interface, "get_collection", new=interface_mocks.get_collection_mock)
    @mock.patch.object(interface, "get_database", new=interface_mocks.get_database_mock)
    @mock.patch.object(interface, "query", new=interface_mocks.query_mock)
    @mock.patch.dict(os.environ, {"GIPHY_TOKEN": "token"})
    def test_main_giphy_env(self) -> None:
        """Tests main function with giphy token set via environment variable."""
        main.DEBUG_MODE = True
        main.TOKEN = "token"
        with mock.patch.object(main.BSEBot, "run"):
            main._main()
