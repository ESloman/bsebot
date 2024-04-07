"""Tests our main.py file."""

import os
from unittest import mock

import discord
import pytest

from discordbot import main
from mongo import interface
from tests.mocks import bsebot_mocks, interface_mocks


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
