"""Tests our main.py file."""

import os
from unittest import mock

import discord
import pytest

from discordbot import main
from tests.mocks import bsebot_mocks


class TestMain:
    """Tests our main.py file."""

    def test_main_no_token(self) -> None:
        """Tests main function with no token."""
        main.DEBUG_MODE = True
        main.TOKEN = None
        with pytest.raises(SystemExit):
            main._main()
