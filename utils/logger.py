"""
Logging utilities for the cocobot application.

This module provides centralized logging configuration and utilities
for consistent logging across the entire application.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_file: str = None,
    max_bytes: int = 10485760,
    backup_count: int = 5,
):
    """
    Set up centralized logging with both file and console handlers.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (optional, defaults to logs/cocobot.log)
        max_bytes: Maximum size of log file before rotation (default 10MB)
        backup_count: Number of backup files to keep
    """
    from logging.handlers import RotatingFileHandler

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    if log_file is None:
        # Default log file path with timestamp
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = logs_dir / f"cocobot_{timestamp}.log"

    # Configure the root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter with more detailed information
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler with rotation for production
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except PermissionError:
        # Fallback if we can't write to log file
        print(
            f"Warning: Cannot write to log file {log_file}, continuing with console only"
        )

    # Suppress overly verbose loggers
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('websockets').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Predefined loggers for common use cases
bot_logger = get_logger('cocobot.bot')
command_logger = get_logger('cocobot.commands')
api_logger = get_logger('cocobot.api')
error_logger = get_logger('cocobot.errors')
