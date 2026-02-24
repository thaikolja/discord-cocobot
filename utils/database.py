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
#  Date:      2014-2026
#  Package:   cocobot Discord Bot

"""
Database models and integration for the cocobot application.

This module provides database models, connection handling, and repository patterns
for persistent data storage.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func

# Create base class for SQLAlchemy models
Base = declarative_base()


class CacheEntry(Base):
    """Cache model for storing cached API responses."""

    __tablename__ = 'cache_entries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    cache_key = Column(String(500), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class RateLimit(Base):
    """Rate limiting model for tracking usage."""

    __tablename__ = 'rate_limits'

    id = Column(Integer, primary_key=True, autoincrement=True)
    identifier = Column(
        String(100), nullable=False, index=True
    )  # User ID, IP, or guild ID
    resource = Column(
        String(100), nullable=False
    )  # The resource being limited (e.g., 'weather', 'translate')
    requests_count = Column(Integer, default=1)
    reset_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class VisaReminder(Base):
    """Visa reminder tracking model for storing user reminder status."""

    __tablename__ = 'visa_reminders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_discord_id = Column(String(32), unique=True, nullable=False, index=True)
    reminded_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class JailedUser(Base):
    """Tracks jailed users with role snapshots for restoration on unjail."""

    __tablename__ = 'jailed_users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    jailed_at = Column(DateTime, server_default=func.now())
    jailed_by = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    roles_snapshot = Column(Text, nullable=False)


# Database session management
_engine = None
_SessionLocal = None


def init_db(database_url: Optional[str] = None) -> None:
    """
    Initialize the database connection.

    Args:
        database_url: Database connection URL. If None, uses environment variable.
    """
    global _engine, _SessionLocal

    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///cocobot.db')

    # Create database engine
    _engine = create_engine(
        database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
    )

    # Create session factory
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

    # Create all tables
    Base.metadata.create_all(bind=_engine)

    # Enforce an immediate connection to strictly write the .db file at startup
    try:
        with _engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to verify database creation: {e}")


def get_db_session():
    """
    Get a database session.

    Yields:
        Database session
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    """
    Get the database engine.

    Returns:
        Database engine instance
    """
    if _engine is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine


class DatabaseManager:
    """High-level database operations manager."""

    @staticmethod
    def get_cache_entry(db, cache_key: str):
        """Get cache entry by key."""
        entry = db.query(CacheEntry).filter(CacheEntry.cache_key == cache_key).first()
        if entry and entry.expires_at < datetime.utcnow():
            # Entry has expired, delete it
            db.delete(entry)
            db.commit()
            return None
        return entry

    @staticmethod
    def set_cache_entry(db, cache_key: str, value: str, ttl_seconds: int = 3600):
        """Set cache entry with TTL."""
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)

        # Check if entry already exists
        existing = (
            db.query(CacheEntry).filter(CacheEntry.cache_key == cache_key).first()
        )
        if existing:
            existing.value = value
            existing.expires_at = expires_at
        else:
            entry = CacheEntry(cache_key=cache_key, value=value, expires_at=expires_at)
            db.add(entry)

        db.commit()

    @staticmethod
    async def async_get_cache_entry(cache_key: str) -> Optional[str]:
        """Asynchronously get cache entry by key, handling its own session execution."""

        def _get():
            with _SessionLocal() as db:
                entry = DatabaseManager.get_cache_entry(db, cache_key)
                if entry:
                    # Access the .value inside the session so it isn't detached
                    return entry.value
                return None

        # Run the synchronous DB operations in a thread
        return await asyncio.to_thread(_get)

    @staticmethod
    async def async_set_cache_entry(cache_key: str, value: str, ttl_seconds: int = 600):
        """Asynchronously set cache entry with TTL, handling its own session execution."""

        def _set():
            with _SessionLocal() as db:
                DatabaseManager.set_cache_entry(db, cache_key, value, ttl_seconds)

        # Run the synchronous DB operations in a thread
        await asyncio.to_thread(_set)

    @staticmethod
    def has_been_reminded_about_visa(db, user_discord_id: str) -> bool:
        """Check if a user has been reminded about mentioning nationality in visa channel."""
        reminder = db.query(VisaReminder).filter(VisaReminder.user_discord_id == user_discord_id).first()
        return reminder is not None

    @staticmethod
    def mark_user_as_reminded_about_visa(db, user_discord_id: str):
        """Mark a user as reminded about mentioning nationality in visa channel."""
        reminder = VisaReminder(user_discord_id=user_discord_id, reminded_at=datetime.utcnow())
        db.add(reminder)
        db.commit()


# Initialize database if this module is imported
if os.getenv('INIT_DB_ON_STARTUP', 'true').lower() == 'true':
    init_db()
