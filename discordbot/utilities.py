
"""
File for other small and useful classes that we may need in other parts of the code
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class PlaceHolderLogger():
    """
    Placeholder logger for when we don't have a logging object
    replaces logging functions with just printing
    """
    @staticmethod
    def info(msg: str) -> None:
        print(msg)

    @staticmethod
    def debug(msg: str) -> None:
        print(msg)

    @staticmethod
    def warning(msg: str) -> None:
        print(msg)


class _ColourFormatter(logging.Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, "\x1b[40;1m"),
        (logging.INFO, "\x1b[34;1m"),
        (logging.WARNING, "\x1b[33;1m"),
        (logging.ERROR, "\x1b[31m"),
        (logging.CRITICAL, "\x1b[41m"),
    ]

    FORMATS = {
        level: logging.Formatter(
            f"\x1b[30;1m[%(asctime)s]\x1b[0m {colour}[%(levelname)s] \x1b[0m\x1b[35m%(funcName)8s:\x1b[0m %(message)s"
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f"\x1b[31m{text}\x1b[0m"

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


def create_logger(level: int = None) -> logging.Logger:
    """
    Creates a simple logger to use throughout the bot
    :return: Logger object
    """
    if not level:
        level = logging.DEBUG

    fol = os.path.join(os.path.expanduser("~"), "bsebotlogs")
    if not os.path.exists(fol):
        os.makedirs(fol)

    _logger = logging.getLogger("bsebot")
    _logger.setLevel(level)

    formatting = "[%(asctime)s] [%(levelname)8s] %(funcName)s: %(message)s"
    formatter = logging.Formatter(formatting)
    colour_formatter = _ColourFormatter()

    # this makes sure we're logging to the standard output too
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(colour_formatter)

    # this makes sure we're logging to a file
    file_handler = RotatingFileHandler(
        os.path.join(fol, "bsebot.log"), maxBytes=10485760, backupCount=1
    )
    file_handler.setFormatter(formatter)

    _logger.addHandler(stream_handler)
    _logger.addHandler(file_handler)

    return _logger
