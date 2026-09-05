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
Custom exception classes for the cocobot application.

This module defines application-specific exceptions that can be used
throughout the codebase for better error handling and debugging.
"""

# Optional so older call sites can omit codes without a stack of Nones
from typing import Optional


# Root of the coconut exception family; catch this if you like wide nets
class CocobotException(Exception):
    """Base exception class for all cocobot-specific exceptions."""

    # Message plus optional code and the exception that started this party
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # Let Exception store the message the usual way
        super().__init__(message)

        # Keep a plain string for logs that don't want the whole object
        self.message = message

        # Machine-friendly code like CONFIG_ERROR, or None if we're feeling lazy
        self.error_code = error_code

        # Chain the original so debug sessions aren't a murder mystery
        self.original_exception = original_exception

    # Pretty print with a bracketed code when we have one
    def __str__(self):

        # Codes make grepping logs slightly less miserable
        if self.error_code:

            # [CODE] human text
            return f"[{self.error_code}] {self.message}"

        # No code: just the message, like a normal Exception
        return self.message


# .env missing, key empty, types that lie
class ConfigurationError(CocobotException):
    """Raised when there's a configuration-related error."""

    # Remember which config key betrayed us
    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # Stamp CONFIG_ERROR so handlers can branch without isinstance gymnastics
        super().__init__(
            message, error_code="CONFIG_ERROR", original_exception=original_exception
        )

        # Which knob was wrong; None if the whole file is on fire
        self.config_key = config_key


# HTTP/API vendors returning 429, 500, or poetry
class APIError(CocobotException):
    """Raised when an API call fails."""

    # Status code and vendor name for the postmortem
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # All API failures wear the same error_code badge
        super().__init__(
            message, error_code="API_ERROR", original_exception=original_exception
        )

        # HTTP status if we got one; timeouts often don't
        self.status_code = status_code

        # weatherapi vs groq vs "that one we copied from Stack Overflow"
        self.api_name = api_name


# Slash command exploded after Discord already acknowledged
class CommandError(CocobotException):
    """Raised when a command execution fails."""

    # Name the command so logs aren't just "a command failed, good luck"
    def __init__(
        self,
        message: str,
        command_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # COMMAND_ERROR for handlers that retry vs give up
        super().__init__(
            message, error_code="COMMAND_ERROR", original_exception=original_exception
        )

        # /time, /learn, whatever the user actually typed
        self.command_name = command_name


# Too many requests; the coconut needs a nap
class RateLimitError(CocobotException):
    """Raised when rate limits are exceeded."""

    # retry_after is the only number Discord actually cares about
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        original_exception: Optional[Exception] = None,
    ):

        # Distinct code so we don't treat rate limits like logic bugs
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            original_exception=original_exception,
        )

        # Seconds to wait, or None if the vendor was unhelpfully vague
        self.retry_after = retry_after


# User input that failed the sniff test
class ValidationError(CocobotException):
    """Raised when input validation fails."""

    # Field name so the user hears "location" not "invalid"
    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # VALIDATION_ERROR: usually the human's fault, occasionally ours
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            original_exception=original_exception,
        )

        # Which argument was cursed
        self.field_name = field_name


# SQLite/async DB hiccups
class DatabaseError(CocobotException):
    """Raised when database operations fail."""

    # operation is get/set/migrate, not a SQL novel
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # Short DB_ERROR code for logs
        super().__init__(
            message, error_code="DB_ERROR", original_exception=original_exception
        )

        # What we were trying to do when the disk said no
        self.operation = operation


# Tokens in the wrong place, permission surprises, etc.
class SecurityError(CocobotException):
    """Raised when a security-related issue occurs."""

    # security_type is a label, not a CVE number
    def __init__(
        self,
        message: str,
        security_type: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):

        # SECURITY_ERROR: treat as fail-closed upstream
        super().__init__(
            message, error_code="SECURITY_ERROR", original_exception=original_exception
        )

        # auth, token, permission — whatever bucket we stuffed this into
        self.security_type = security_type
