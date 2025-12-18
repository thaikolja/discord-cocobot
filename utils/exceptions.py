"""
Custom exception classes for the cocobot application.

This module defines application-specific exceptions that can be used
throughout the codebase for better error handling and debugging.
"""

from typing import Optional


class CocobotException(Exception):
    """Base exception class for all cocobot-specific exceptions."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.original_exception = original_exception

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ConfigurationError(CocobotException):
    """Raised when there's a configuration-related error."""

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message, error_code="CONFIG_ERROR", original_exception=original_exception
        )
        self.config_key = config_key


class APIError(CocobotException):
    """Raised when an API call fails."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        api_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message, error_code="API_ERROR", original_exception=original_exception
        )
        self.status_code = status_code
        self.api_name = api_name


class CommandError(CocobotException):
    """Raised when a command execution fails."""

    def __init__(
        self,
        message: str,
        command_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message, error_code="COMMAND_ERROR", original_exception=original_exception
        )
        self.command_name = command_name


class RateLimitError(CocobotException):
    """Raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message,
            error_code="RATE_LIMIT_ERROR",
            original_exception=original_exception,
        )
        self.retry_after = retry_after


class ValidationError(CocobotException):
    """Raised when input validation fails."""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            original_exception=original_exception,
        )
        self.field_name = field_name


class DatabaseError(CocobotException):
    """Raised when database operations fail."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message, error_code="DB_ERROR", original_exception=original_exception
        )
        self.operation = operation


class SecurityError(CocobotException):
    """Raised when a security-related issue occurs."""

    def __init__(
        self,
        message: str,
        security_type: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(
            message, error_code="SECURITY_ERROR", original_exception=original_exception
        )
        self.security_type = security_type
