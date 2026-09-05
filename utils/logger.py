#  Copyright (C) 2026 by Kolja Nolte
#  kolja.nolte@gmail.com
#  https://gitlab.com/thailand-discord/bots/cocobot
#
#  This work is licensed under the MIT License. You are free to use, copy, modify,
#  merge, publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so, subject to the
#  condition that the above copyright notice and this permission notice shall be
#  included in all
#  copies or substantial portions of the Software.
#
#  For more information, visit: https://opensource.org/licenses/MIT
#
#  Author:    Kolja Nolte
#  Email:     kolja.nolte@gmail.com
#  License:   MIT
#  Date:      2024-2026
#  Package:   cocobot Discord Bot

"""
Logging utilities for the cocobot application.

This module provides centralized logging configuration and utilities
for consistent logging across the entire application.
"""

# stdlib logging: the grown-up print()
import logging

# Env vars for log level without a redeploy ritual
import os

# stdout for the console handler, because stderr is already crowded
import sys

# Timestamps for daily log filenames
from datetime import datetime

# Path so "logs/" isn't a string we keep misspelling
from pathlib import Path


# Wire file + console handlers once, then everyone else just get_logger()
def setup_logging(
    log_level: str = os.getenv("LOG_LEVEL", "WARNING"),
    log_file: str = None,
    max_bytes: int = 10485760,
    backup_count: int = int(os.getenv("LOG_BACKUP_COUNT", "5")),
):
    """
    Set up centralized logging with both file and console handlers.

    Args:
        log_level: The logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file (optional, defaults to logs/cocobot.log)
        max_bytes: Maximum size of log file before rotation (default 10MB)
        backup_count: Number of backup files to keep
    """

    # Import here so importing this module doesn't drag handlers into tests by accident
    from logging.handlers import RotatingFileHandler

    # Logs live in ./logs, not sprinkled across the repo like confetti
    logs_dir = Path("logs")

    # mkdir is cheap; missing directories are not
    logs_dir.mkdir(exist_ok=True)

    # Caller didn't pick a file, so we invent a dated one
    if log_file is None:
        # One file per calendar day, not per millisecond of anxiety
        timestamp = datetime.now().strftime("%Y%m%d")

        # cocobot_YYYYMMDD.log — boring, searchable, good
        log_file = logs_dir / f"cocobot_{timestamp}.log"

    # Root logger: the one everyone inherits unless they rebel
    logger = logging.getLogger()

    # Honor LOG_LEVEL even if someone typed "info" in pajamas
    logger.setLevel(getattr(logging, log_level.upper()))

    # Copy the list; mutating while iterating is how you invent Heisenbugs
    for handler in logger.handlers[:]:
        # Strip leftovers from a previous setup_logging call
        logger.removeHandler(handler)

    # Timestamp, level, module, line — the forensic kit
    formatter = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Console so systemd/docker logs aren't empty
    console_handler = logging.StreamHandler(sys.stdout)

    # Same level as root; no secret DEBUG on stdout unless asked
    console_handler.setLevel(getattr(logging, log_level.upper()))

    # Attach the shared formatter
    console_handler.setFormatter(formatter)

    # Root hears the console now
    logger.addHandler(console_handler)

    # Disk might be read-only; don't let that kill the bot
    try:

        # Rotate at ~10MB so one verbose night doesn't eat the disk
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8'
        )

        # File stays at INFO even if console is WARNING — future-you will thank us
        file_handler.setLevel(logging.INFO)

        # Same format as console so grepping feels consistent
        file_handler.setFormatter(formatter)

        # Root also writes to disk
        logger.addHandler(file_handler)

    # Container users without a writable logs/ dir
    except PermissionError:

        # Don't raise; a coconut that can't log to disk can still talk
        print(
            f"Warning: Cannot write to log file {log_file}, continuing with console only"
        )

    # discord.py is chatty; we want INFO, not gateway heartbeat poetry
    discord_logger = logging.getLogger('discord')

    # Cap discord at INFO
    discord_logger.setLevel(logging.INFO)

    # Remove handlers discord.py may have bolted on
    for handler in discord_logger.handlers[:]:
        # One handler to rule them, not five copies of the same line
        discord_logger.removeHandler(handler)

    # Stop bubbling into root or every message prints twice like a bad echo
    discord_logger.propagate = False

    # Dedicated console for discord.* so we still see connection drama
    discord_console = logging.StreamHandler(sys.stdout)

    # Same format; mixed log styles are a tax on the reader
    discord_console.setFormatter(formatter)

    # Attach it
    discord_logger.addHandler(discord_console)

    # Client internals: WARNING unless the websocket is actually on fire
    logging.getLogger('discord.client').setLevel(logging.WARNING)

    # Gateway heartbeats are not news
    logging.getLogger('discord.gateway').setLevel(logging.WARNING)

    # websockets library: shh
    logging.getLogger('websockets').setLevel(logging.WARNING)

    # aiohttp access noise belongs in a museum
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


# Thin wrapper so call sites don't import logging everywhere
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """

    # Named child of root; setup_logging already configured the parents
    return logging.getLogger(name)


# Bot lifecycle: ready, disconnect, "why is it looping"
bot_logger = get_logger('cocobot.bot')

# Slash/prefix command traces
command_logger = get_logger('cocobot.commands')

# Outbound HTTP to weather, time, LLMs, etc.
api_logger = get_logger('cocobot.api')

# Dedicated errors logger for the "something cracked" pile
error_logger = get_logger('cocobot.errors')
