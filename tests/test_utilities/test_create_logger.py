"""Tests our utility create logger funciton."""

from logging import DEBUG, INFO, Logger

from discordbot.utilities import create_logger


class TestCreateLogger:
    @staticmethod
    def test_simple_create() -> None:
        """Tests creating a logger with no input."""
        logger = create_logger()
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        assert isinstance(logger, Logger)
        assert logger.level == DEBUG

    @staticmethod
    def test_create_with_level() -> None:
        """Tests creating a logger with a specified level."""
        logger = create_logger(INFO)
        logger.info("Info")
        logger.debug("Debug")
        logger.warning("Warning")
        logger.critical("Critical")
        assert isinstance(logger, Logger)
        assert logger.level == INFO
