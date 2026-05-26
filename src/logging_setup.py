"""Logging configuration for the water quality system."""

import sys
from pathlib import Path

from loguru import logger

from src.config import settings


def setup_logging():
    """Configure logging for the application.

    Sets up console and file logging with rotation and formatting.
    """
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Console handler (colorized)
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - {message}",
        level=settings.log_level,
        colorize=True,
    )

    # File handler (rotating)
    logger.add(
        log_dir / "system_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="1 day",
        retention="30 days",
        compression="zip",
        encoding="utf-8",
    )

    logger.info("Logging initialized (level: {})", settings.log_level)
    return logger


# Initialize on import
setup_logging()
