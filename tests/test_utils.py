"""
Test utilities for the cocobot application.

This module provides utilities for testing including mock objects,
test fixtures, and helper functions.
"""

import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock
from contextlib import contextmanager
from typing import Any, Dict, Optional
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from utils.database import Base, User, Guild, CommandUsage


class MockDiscordObjects:
    """Mock Discord objects for testing."""
    
    @staticmethod
    def create_mock_user(id: str = "123456789", name: str = "testuser", discriminator: str = "0001"):
        """Create a mock Discord user object."""
        user = Mock()
        user.id = id
        user.name = name
        user.discriminator = discriminator
        user.mention = f"<@{id}>"
        return user
    
    @staticmethod
    def create_mock_interaction(
        command_name: str = "test_command",
        user_id: str = "123456789",
        guild_id: Optional[str] = "987654321",
        channel_id: str = "555666777",
        response_data: Optional[Dict] = None
    ):
        """Create a mock Discord interaction object."""
        interaction = Mock()
        interaction.command.name = command_name
        interaction.user = MockDiscordObjects.create_mock_user(user_id)
        interaction.guild_id = guild_id
        interaction.channel_id = channel_id
        
        # Mock response methods
        if response_data is None:
            response_data = {"success": True}
        
        interaction.response = Mock()
        interaction.response.send_message = AsyncMock()
        interaction.followup = Mock()
        interaction.followup.send = AsyncMock()
        
        # Add response data to the mock
        for key, value in response_data.items():
            setattr(interaction, key, value)
        
        return interaction
    
    @staticmethod
    def create_mock_context(
        command_name: str = "test_command",
        user_id: str = "123456789",
        guild_id: Optional[str] = "987654321",
        channel_id: str = "555666777"
    ):
        """Create a mock Discord context object."""
        ctx = Mock()
        ctx.command = Mock()
        ctx.command.name = command_name
        ctx.author = MockDiscordObjects.create_mock_user(user_id)
        ctx.guild = Mock()
        ctx.guild.id = guild_id
        ctx.channel = Mock()
        ctx.channel.id = channel_id
        ctx.send = AsyncMock()
        return ctx


class DatabaseTestUtils:
    """Test database utilities."""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def setup_test_db(self):
        """Set up an in-memory test database."""
        self.engine = create_engine(
            "sqlite:///:memory:",
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(bind=self.engine)
        
        return self.engine, self.SessionLocal
    
    @contextmanager
    def get_test_db_session(self):
        """Get a test database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Test database not initialized. Call setup_test_db() first.")
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


class AsyncMockWithSpec(AsyncMock):
    """AsyncMock that preserves function signature."""
    
    def __init__(self, func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preserve the original function's signature if possible
        if callable(func):
            self.__name__ = getattr(func, '__name__', 'async_mock')
            self.__doc__ = getattr(func, '__doc__', 'Async mock function')


def async_test(f):
    """Decorator to run async tests."""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper


@pytest.fixture
def mock_discord_objects():
    """Pytest fixture for mock Discord objects."""
    return MockDiscordObjects


@pytest.fixture
def test_db():
    """Pytest fixture for test database."""
    test_db_util = TestDatabase()
    engine, session_local = test_db_util.setup_test_db()
    
    yield test_db_util
    
    # Cleanup would happen here if needed


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "discord_id": "123456789012345678",
        "username": "testuser",
        "discriminator": "1234",
        "is_premium": False
    }


@pytest.fixture
def sample_guild_data():
    """Sample guild data for testing."""
    return {
        "discord_id": "987654321098765432",
        "name": "Test Guild",
        "owner_id": "111222333444555666"
    }


def create_mock_api_response(status: int = 200, json_data: Optional[Dict] = None):
    """Create a mock API response object."""
    if json_data is None:
        json_data = {"result": "success"}
    
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=json_data)
    mock_response.text = AsyncMock(return_value=str(json_data))
    mock_response.raise_for_status = Mock() if status < 400 else Mock(side_effect=Exception("HTTP Error"))
    
    return mock_response


def mock_api_call(api_func, return_value: Any = None, side_effect: Any = None):
    """Helper to mock an API call function."""
    if side_effect:
        api_func = AsyncMock(side_effect=side_effect)
    else:
        api_func = AsyncMock(return_value=return_value)
    return api_func


class TestHelpers:
    """Additional test helper functions."""
    
    @staticmethod
    def assert_model_attributes(model_instance, expected_attrs: Dict[str, Any]):
        """Assert that model instance has expected attributes."""
        for attr_name, expected_value in expected_attrs.items():
            actual_value = getattr(model_instance, attr_name)
            assert actual_value == expected_value, f"Expected {attr_name}={expected_value}, got {actual_value}"
    
    @staticmethod
    def create_sample_user(db_session, **overrides):
        """Create a sample user in the test database."""
        user_data = {
            "discord_id": "123456789012345678",
            "username": "testuser",
            "discriminator": "1234"
        }
        user_data.update(overrides)
        
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        return user
    
    @staticmethod
    def create_sample_guild(db_session, **overrides):
        """Create a sample guild in the test database."""
        guild_data = {
            "discord_id": "987654321098765432",
            "name": "Test Guild",
            "owner_id": "111222333444555666"
        }
        guild_data.update(overrides)
        
        guild = Guild(**guild_data)
        db_session.add(guild)
        db_session.commit()
        db_session.refresh(guild)
        
        return guild


# Global test utilities instance
test_helpers = TestHelpers()