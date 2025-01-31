import sys
from enum import StrEnum

from loguru import logger


class LogLevel(StrEnum):
    """A simple class to handle the logging level."""

    NONE = ""
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @staticmethod
    def set(level: "LogLevel") -> None:
        """Set the logging level.

        Args:
            level (LogLevel): the wanted logging level.
        """
        logger.remove()
        if level != LogLevel.NONE:
            logger.add(sys.stderr, level=level.value)
