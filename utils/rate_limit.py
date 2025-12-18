"""
Database-backed rate limiting utilities for the cocobot application.

This module provides persistent rate limiting functionality to prevent abuse
and manage API usage effectively across restarts.
"""

import logging
import threading
import time
from enum import Enum
from typing import Dict, Optional, Tuple

from .database import RateLimit, get_db_session


class RateLimitType(Enum):
    """Types of rate limits."""

    USER = "user"
    GUILD = "guild"
    CHANNEL = "channel"
    GLOBAL = "global"


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, message: str, retry_after: float, resource: str):
        super().__init__(message)
        self.retry_after = retry_after
        self.resource = resource


class DatabaseRateLimiter:
    """Database-backed rate limiter for persistent tracking."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def is_allowed(
        self, identifier: str, resource: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, float]:
        """
        Check if a request is allowed based on database-stored rate limits.

        Args:
                        identifier: The entity being limited (user ID, guild ID, etc.)
                        resource: The resource being accessed (command name, API endpoint, etc.)
                        max_requests: Maximum number of requests allowed
                        window_seconds: Time window in seconds

        Returns:
                        Tuple of (is_allowed, retry_after_seconds)
        """
        from datetime import datetime, timedelta

        with get_db_session() as db:
            # Get existing rate limit record
            rate_limit = (
                db.query(RateLimit)
                .filter(
                    RateLimit.identifier == identifier, RateLimit.resource == resource
                )
                .first()
            )

            if rate_limit is None:
                # Create new rate limit record
                rate_limit = RateLimit(
                    identifier=identifier,
                    resource=resource,
                    requests_count=1,
                    reset_at=datetime.utcnow() + timedelta(seconds=window_seconds),
                )
                db.add(rate_limit)
                db.commit()
                return True, 0.0

            # Check if the window has reset
            if datetime.utcnow() > rate_limit.reset_at:
                # Reset the counter
                rate_limit.requests_count = 1
                rate_limit.reset_at = datetime.utcnow() + timedelta(
                    seconds=window_seconds
                )
                db.commit()
                return True, 0.0

            # Check if limit is exceeded
            if rate_limit.requests_count >= max_requests:
                # Calculate retry after time
                time_since_reset = datetime.utcnow() - (
                    rate_limit.reset_at - timedelta(seconds=window_seconds)
                )
                elapsed = time_since_reset.total_seconds()
                retry_after = max(0, window_seconds - elapsed)

                self.logger.warning(
                    f"Rate limit exceeded for {identifier} on resource {resource}"
                )
                return False, retry_after

            # Increment request count
            rate_limit.requests_count += 1
            db.commit()

            return True, 0.0

    def reset_limit(self, identifier: str, resource: str):
        """Reset rate limit for a specific identifier and resource."""
        with get_db_session() as db:
            rate_limit = (
                db.query(RateLimit)
                .filter(
                    RateLimit.identifier == identifier, RateLimit.resource == resource
                )
                .first()
            )

            if rate_limit:
                db.delete(rate_limit)
                db.commit()


class InMemoryRateLimiter:
    """In-memory rate limiter for temporary tracking."""

    def __init__(self):
        self.limits: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def is_allowed(
        self, identifier: str, resource: str, max_requests: int, window_seconds: int
    ) -> Tuple[bool, float]:
        """
        Check if a request is allowed based on in-memory rate limits.

        Args:
                        identifier: The entity being limited (user ID, guild ID, etc.)
                        resource: The resource being accessed (command name, API endpoint, etc.)
                        max_requests: Maximum number of requests allowed
                        window_seconds: Time window in seconds

        Returns:
                        Tuple of (is_allowed, retry_after_seconds)
        """
        key = f"{identifier}:{resource}"

        with self._lock:
            now = time.time()
            window_start = now - window_seconds

            if key not in self.limits:
                self.limits[key] = {'requests': [], 'window_start': now}

            # Remove old requests outside the window
            self.limits[key]['requests'] = [
                req_time
                for req_time in self.limits[key]['requests']
                if req_time > window_start
            ]

            # Check if limit is exceeded
            if len(self.limits[key]['requests']) >= max_requests:
                # Calculate when the next request will be allowed
                oldest_request = self.limits[key]['requests'][0]
                retry_after = oldest_request + window_seconds - now
                return False, max(0, retry_after)

            # Add current request to the list
            self.limits[key]['requests'].append(now)
            return True, 0.0

    def reset_limit(self, identifier: str, resource: str):
        """Reset rate limit for a specific identifier and resource."""
        key = f"{identifier}:{resource}"
        with self._lock:
            if key in self.limits:
                del self.limits[key]


class HybridRateLimiter:
    """Hybrid rate limiter that uses both in-memory and database storage."""

    def __init__(self):
        self.in_memory_limiter = InMemoryRateLimiter()
        self.db_limiter = DatabaseRateLimiter()
        self.logger = logging.getLogger(__name__)

    def is_allowed(
        self,
        identifier: str,
        resource: str,
        max_requests: int,
        window_seconds: int,
        use_db: bool = True,
    ) -> Tuple[bool, float]:
        """
        Check if a request is allowed using both in-memory and database rate limits.

        Args:
                        identifier: The entity being limited
                        resource: The resource being accessed
                        max_requests: Maximum number of requests allowed
                        window_seconds: Time window in seconds
                        use_db: Whether to also check database limits

        Returns:
                        Tuple of (is_allowed, retry_after_seconds)
        """
        # Check in-memory rate limit first (faster)
        mem_allowed, mem_retry_after = self.in_memory_limiter.is_allowed(
            identifier, resource, max_requests, window_seconds
        )

        if not mem_allowed:
            return False, mem_retry_after

        # If in-memory allows it, also check database if requested
        if use_db:
            db_allowed, db_retry_after = self.db_limiter.is_allowed(
                identifier, resource, max_requests, window_seconds
            )
            if not db_allowed:
                return False, db_retry_after

        return True, 0.0

    def reset_limit(self, identifier: str, resource: str, use_db: bool = True):
        """Reset rate limit for a specific identifier and resource."""
        self.in_memory_limiter.reset_limit(identifier, resource)
        if use_db:
            self.db_limiter.reset_limit(identifier, resource)


# Global rate limiter instance
_global_rate_limiter = HybridRateLimiter()


def get_global_rate_limiter() -> HybridRateLimiter:
    """Get the global rate limiter instance."""
    return _global_rate_limiter


def check_rate_limit(
    identifier: str,
    resource: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    raise_exception: bool = True,
    use_db: bool = True,
) -> bool:
    """
    Check if a rate limit would be exceeded.

    Args:
                    identifier: The entity being limited
                    resource: The resource being accessed
                    max_requests: Max requests in the window
                    window_seconds: Time window in seconds
                    raise_exception: Whether to raise exception if limit exceeded
                    use_db: Whether to use database persistence

    Returns:
                    True if allowed, False if exceeded (when raise_exception=False)

    Raises:
                    RateLimitExceeded: If limit exceeded and raise_exception=True
    """
    is_allowed, retry_after = _global_rate_limiter.is_allowed(
        identifier, resource, max_requests, window_seconds, use_db
    )

    if not is_allowed and raise_exception:
        raise RateLimitExceeded(
            f"Rate limit exceeded for {resource}", retry_after, resource
        )

    return is_allowed


def user_rate_limit(
    user_id: str,
    resource: str,
    max_requests: int = 10,
    window_seconds: int = 60,
    raise_exception: bool = True,
    use_db: bool = True,
) -> bool:
    """
    Check rate limit for a specific user.

    Args:
                    user_id: Discord user ID
                    resource: Resource being accessed
                    max_requests: Max requests in the window
                    window_seconds: Time window in seconds
                    raise_exception: Whether to raise exception if limit exceeded
                    use_db: Whether to use database persistence

    Returns:
                    True if allowed, False if exceeded (when raise_exception=False)
    """
    return check_rate_limit(
        f"user:{user_id}",
        resource,
        max_requests,
        window_seconds,
        raise_exception,
        use_db,
    )


def channel_rate_limit(
    channel_id: str,
    resource: str,
    max_requests: int = 15,
    window_seconds: int = 60,
    raise_exception: bool = True,
    use_db: bool = True,
) -> bool:
    """
    Check rate limit for a specific channel.

    Args:
                    channel_id: Discord channel ID
                    resource: Resource being accessed
                    max_requests: Max requests in the window
                    window_seconds: Time window in seconds
                    raise_exception: Whether to raise exception if limit exceeded
                    use_db: Whether to use database persistence

    Returns:
                    True if allowed, False if exceeded (when raise_exception=False)
    """
    return check_rate_limit(
        f"channel:{channel_id}",
        resource,
        max_requests,
        window_seconds,
        raise_exception,
        use_db,
    )


def guild_rate_limit(
    guild_id: str,
    resource: str,
    max_requests: int = 50,
    window_seconds: int = 60,
    raise_exception: bool = True,
    use_db: bool = True,
) -> bool:
    """
    Check rate limit for a specific guild.

    Args:
                    guild_id: Discord guild ID
                    resource: Resource being accessed
                    max_requests: Max requests in the window
                    window_seconds: Time window in seconds
                    raise_exception: Whether to raise exception if limit exceeded
                    use_db: Whether to use database persistence

    Returns:
                    True if allowed, False if exceeded (when raise_exception=False)
    """
    return check_rate_limit(
        f"guild:{guild_id}",
        resource,
        max_requests,
        window_seconds,
        raise_exception,
        use_db,
    )


def global_rate_limit(
    resource: str,
    max_requests: int = 100,
    window_seconds: int = 60,
    raise_exception: bool = True,
    use_db: bool = True,
) -> bool:
    """
    Check global rate limit for a resource.

    Args:
                    resource: Resource being accessed
                    max_requests: Max requests in the window
                    window_seconds: Time window in seconds
                    raise_exception: Whether to raise exception if limit exceeded
                    use_db: Whether to use database persistence

    Returns:
                    True if allowed, False if exceeded (when raise_exception=False)
    """
    return check_rate_limit(
        "global", resource, max_requests, window_seconds, raise_exception, use_db
    )


class CommandRateLimiter:
    """Rate limiter specifically for commands."""

    def __init__(self, default_commands_per_minute: int = 10):
        self.default_commands_per_minute = default_commands_per_minute
        self.rate_limiter = _global_rate_limiter
        self.logger = logging.getLogger(__name__)

    def check_command_limit(
        self,
        user_id: str,
        command_name: str,
        max_requests: Optional[int] = None,
        use_db: bool = True,
    ) -> Tuple[bool, float]:
        """
        Check if a command can be executed by a user.

        Args:
                        user_id: Discord user ID
                        command_name: Name of the command
                        max_requests: Max requests per minute (uses default if None)
                        use_db: Whether to use database persistence

        Returns:
                        Tuple of (is_allowed, retry_after_seconds)
        """
        if max_requests is None:
            max_requests = self.default_commands_per_minute

        return self.rate_limiter.is_allowed(
            f"user:{user_id}",
            f"command:{command_name}",
            max_requests,
            60,  # 60 seconds window
            use_db,
        )

    def check_global_command_limit(
        self, max_requests: int = 100, use_db: bool = True
    ) -> Tuple[bool, float]:
        """
        Check global command rate limit.

        Args:
                        max_requests: Max commands globally per minute
                        use_db: Whether to use database persistence

        Returns:
                        Tuple of (is_allowed, retry_after_seconds)
        """
        return self.rate_limiter.is_allowed(
            "global", "commands", max_requests, 60, use_db  # 60 seconds window
        )


# Global command rate limiter instance
_global_command_rate_limiter = CommandRateLimiter()


def get_command_rate_limiter() -> CommandRateLimiter:
    """Get the global command rate limiter instance."""
    return _global_command_rate_limiter
