"""
Database models and integration for the cocobot application.

This module provides database models, connection handling, and repository patterns
for persistent data storage.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
import os


# Create base class for SQLAlchemy models
Base = declarative_base()


class User(Base):
    """User model for storing user information."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String(32), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    discriminator = Column(String(4), nullable=True)  # For legacy Discord tags
    avatar_url = Column(Text, nullable=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_command_at = Column(DateTime, nullable=True)


class Guild(Base):
    """Guild model for storing server information."""
    __tablename__ = 'guilds'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    discord_id = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    owner_id = Column(String(32), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    prefix = Column(String(10), default='!')


class CommandUsage(Base):
    """Command usage tracking model."""
    __tablename__ = 'command_usage'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    command_name = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Foreign key to users table
    guild_id = Column(Integer, nullable=True, index=True)  # Foreign key to guilds table
    channel_id = Column(String(32), nullable=False)
    executed_at = Column(DateTime, server_default=func.now())
    execution_time_ms = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)


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
    identifier = Column(String(100), nullable=False, index=True)  # User ID, IP, or guild ID
    resource = Column(String(100), nullable=False)  # The resource being limited (e.g., 'weather', 'translate')
    requests_count = Column(Integer, default=1)
    reset_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class BotSetting(Base):
    """Bot settings model for storing configuration values."""
    __tablename__ = 'bot_settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


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
        echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
    )
    
    # Create session factory
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    # Create all tables
    Base.metadata.create_all(bind=_engine)


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
    def get_user_by_discord_id(db, discord_id: str):
        """Get user by Discord ID."""
        return db.query(User).filter(User.discord_id == discord_id).first()
    
    @staticmethod
    def create_or_update_user(db, discord_id: str, username: str, discriminator: Optional[str] = None, avatar_url: Optional[str] = None):
        """Create or update user in the database."""
        user = DatabaseManager.get_user_by_discord_id(db, discord_id)
        if user:
            user.username = username
            user.discriminator = discriminator
            user.avatar_url = avatar_url
            user.updated_at = datetime.utcnow()
        else:
            user = User(
                discord_id=discord_id,
                username=username,
                discriminator=discriminator,
                avatar_url=avatar_url
            )
            db.add(user)
        
        db.commit()
        return user
    
    @staticmethod
    def log_command_usage(db, command_name: str, user_id: int, guild_id: Optional[int], channel_id: str, 
                         execution_time_ms: Optional[float] = None, success: bool = True, error_message: Optional[str] = None):
        """Log command usage in the database."""
        usage = CommandUsage(
            command_name=command_name,
            user_id=user_id,
            guild_id=guild_id,
            channel_id=channel_id,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message
        )
        db.add(usage)
        db.commit()
        return usage
    
    @staticmethod
    def get_cache_entry(db, cache_key: str):
        """Get cache entry by key."""
        from datetime import datetime
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
        from datetime import datetime, timedelta
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        
        # Check if entry already exists
        existing = db.query(CacheEntry).filter(CacheEntry.cache_key == cache_key).first()
        if existing:
            existing.value = value
            existing.expires_at = expires_at
        else:
            entry = CacheEntry(cache_key=cache_key, value=value, expires_at=expires_at)
            db.add(entry)
        
        db.commit()
    
    @staticmethod
    def get_setting(db, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get bot setting by key."""
        setting = db.query(BotSetting).filter(BotSetting.key == key).first()
        if setting:
            return setting.value
        return default
    
    @staticmethod
    def set_setting(db, key: str, value: str, description: Optional[str] = None):
        """Set bot setting."""
        setting = db.query(BotSetting).filter(BotSetting.key == key).first()
        if setting:
            setting.value = value
            setting.description = description
            setting.updated_at = datetime.utcnow()
        else:
            setting = BotSetting(key=key, value=value, description=description)
            db.add(setting)
        
        db.commit()


# Initialize database if this module is imported
if os.getenv('INIT_DB_ON_STARTUP', 'true').lower() == 'true':
    init_db()