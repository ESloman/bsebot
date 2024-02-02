"""Tests our PlaceHolderLogger class."""

from discordbot.utilities import PlaceHolderLogger


class TestPlaceHolderLogger:
    """Tests the placeholder logger."""

    @staticmethod
    def test_logger_static() -> None:
        """Tests the static nature of our class."""
        for attr in ["info", "debug", "warning", "exception"]:
            assert attr in PlaceHolderLogger.__dict__
        PlaceHolderLogger.info("Info")
        PlaceHolderLogger.warning("Warning")
        PlaceHolderLogger.debug("Debug")
        PlaceHolderLogger.exception("Exception")

    @staticmethod
    def test_logger_init() -> None:
        """Tests an instance of our class."""
        logger = PlaceHolderLogger()
        for attr in ["info", "debug", "warning", "exception"]:
            assert getattr(logger, attr) is not None
        logger.info("Info")
        logger.warning("Warning")
        logger.debug("Debug")
        logger.exception("Exception")
