"""Structured logging configuration."""

import logging
import sys

from app.config.settings import Settings


def configure_logging(settings: Settings) -> None:
    """Configure root logger based on application settings."""
    root = logging.getLogger()
    root.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_format == "json":
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )

    handler.setFormatter(formatter)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger for the calling module."""
    return logging.getLogger(name)
